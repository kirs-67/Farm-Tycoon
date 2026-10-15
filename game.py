"""Game rules for Bukid Tycoon. NO Tkinter in this file, so it can be unit-tested.

The interface (ui.py) only calls the methods of FarmGame and shows what they return.
Every action method returns a pair:  (ok, message)
    ok       True if the action worked, False if it was not allowed
    message  a sentence the interface shows to the player

Where the course concepts live in THIS file (see FEATURE_MAP.md):
    Bubble Sort     market_ranking()      ranks discovered crops by today's price
    Insertion Sort  harvest()             inserts each crate into the ordered Bodega
    Selection Sort  soonest_plot()        finds the crop with the least growth time left
                    sell_best()           finds the crate with the highest price today
    Tuple           plot coordinates (row, col) are the keys of self.plots
    Set             self.discovered, self.achievements, self.upgrades, self.owned_fields
    Dictionary      CROPS data, self.plots, self.index (price multipliers), counts
    Recursion       harvest_zone(), ready_value()  (they call zones.collect_cells / sum_values)
"""

import random

import algorithms
import data
import zones


class FarmGame:
    def __init__(self, seed=None, events=True, difficulty="Normal"):
        self.rng = random.Random(seed)
        self.difficulty = difficulty
        self.events_on = events      # tests switch random events off for predictable results
        self.tree = zones.build_farm_tree()
        self.new_game()

    # ------------------------------------------------------------------
    # Setup / restart
    # ------------------------------------------------------------------
    def new_game(self):
        """Reset everything. Used at the start and by the Restart button."""
        self.goal = data.DIFFICULTIES[self.difficulty]
        self.day = 1
        self.coins = data.START_COINS
        self.over = False
        self.won = False

        # DICTIONARY with TUPLE keys: (row, col) -> plot dictionary, or None if empty
        self.plots = {}
        for row in range(data.GRID_ROWS):
            for col in range(data.GRID_COLS):
                self.plots[(row, col)] = None

        # SETS: unique things, no duplicates possible
        self.owned_fields = {0}
        self.upgrades = set()
        self.achievements = set()
        self.discovered = {name for name, crop in data.CROPS.items() if crop["start"]}

        # DICTIONARY: price multiplier for each crop (1.0 = normal price)
        self.index = {name: 1.0 for name in data.CROPS}

        self.bodega = []          # the ordered market inventory (best crates first)
        self.stats = {"harvested": 0, "sold": 0, "earned": 0, "lost": 0}
        self.feed = []            # (day, text) news feed for the player
        self.today_event = None   # (event_name, text) shown as a banner
        self.lab = {"bubble": [], "insertion": [], "selection": []}  # last algorithm steps
        self.say("Welcome to the farm! Plant something, water it, and end the day.")

    def set_difficulty(self, name):
        """Choose Easy / Normal / Hard and start a fresh game."""
        self.difficulty = name
        self.new_game()

    def say(self, text):
        self.feed.append((self.day, text))
        if len(self.feed) > 60:
            self.feed.pop(0)

    # ------------------------------------------------------------------
    # Small helpers
    # ------------------------------------------------------------------
    def capacity(self):
        extra = data.BODEGA_BONUS if "Bodega" in self.upgrades else 0
        return data.BASE_CAPACITY + extra

    def grow_days(self, crop_name):
        days = data.CROPS[crop_name]["grow"]
        if "Irrigation" in self.upgrades:
            days = max(2, days - 1)
        return days

    def is_fiesta(self):
        return self.day in data.FIESTA_DAYS

    def sell_multiplier(self):
        return 1.5 if self.is_fiesta() else 1.0

    def price_of(self, crop_name, quality="Normal"):
        """What one crate of this crop and quality sells for right now."""
        base = data.CROPS[crop_name]["price"]
        value = base * self.index[crop_name] * data.QUALITY[quality] * self.sell_multiplier()
        return max(1, round(value))

    def remaining(self, cell):
        plot = self.plots[cell]
        if plot is None:
            return None
        return max(0, plot["grow"] - plot["age"])

    def is_ready(self, cell):
        plot = self.plots[cell]
        return plot is not None and plot["age"] >= plot["grow"]

    def is_unlocked(self, cell):
        return zones.field_of(cell) in self.owned_fields

    def crop_counts(self):
        """DICTIONARY of how many crates of each crop are stored: {crop: quantity}."""
        counts = {}
        for crate in self.bodega:
            counts[crate["crop"]] = counts.get(crate["crop"], 0) + 1
        return counts

    def all_cells(self):
        """Every plot coordinate in row-major order (plain loops, no sorting needed)."""
        cells = []
        for row in range(data.GRID_ROWS):
            for col in range(data.GRID_COLS):
                cells.append((row, col))
        return cells

    def unlock(self, name):
        if name not in self.achievements:
            self.achievements.add(name)
            self.say("Achievement unlocked: " + name + "!")

    def discover(self, crop_name):
        """Add a crop to the discovered SET. Returns True if it was new."""
        if crop_name in self.discovered:
            return False
        self.discovered.add(crop_name)
        self.say("New crop discovered: " + crop_name + "!")
        if len(self.discovered) == len(data.CROPS):
            self.unlock("Naturalist")
        return True

    # ------------------------------------------------------------------
    # Planting and watering
    # ------------------------------------------------------------------
    def plant(self, cell, crop_name):
        if self.over:
            return False, "The season is over."
        if not self.is_unlocked(cell):
            return False, "You have not bought this field yet."
        if self.plots[cell] is not None:
            return False, "That plot is already planted."
        if crop_name not in self.discovered:
            return False, crop_name + " is not discovered yet. Try a Mystery Seed Packet!"
        seed = data.CROPS[crop_name]["seed"]
        if self.coins < seed:
            return False, "Not enough coins (seeds cost P" + str(seed) + ")."
        self.coins -= seed
        self.plots[cell] = {"crop": crop_name, "age": 0, "grow": self.grow_days(crop_name),
                            "watered_days": 0, "watered_today": False}
        return True, "Planted " + crop_name + " at " + str(cell) + "."

    def smart_action(self, cell, crop_name):
        """One click does the sensible thing for that plot.

        empty plot -> plant the chosen crop | ready crop -> harvest it | thirsty crop -> water it.
        Returns (ok, message, kind) where kind is "plant", "harvest", "water" or "info".
        """
        plot = self.plots[cell]
        if not self.is_unlocked(cell):
            return False, "This field is locked.", "info"
        if plot is None:
            ok, message = self.plant(cell, crop_name)
            return ok, message, "plant"
        if self.is_ready(cell):
            ok, message = self.harvest(cell)
            return ok, message, "harvest"
        if plot["watered_today"]:
            return False, plot["crop"] + " is already watered today.", "info"
        ok, message = self.water(cell)
        return ok, message, "water"

    def water(self, cell):
        plot = self.plots[cell]
        if self.over:
            return False, "The season is over."
        if plot is None:
            return False, "Nothing to water here."
        if plot["age"] >= plot["grow"]:
            return False, "That crop is already ready to harvest."
        if plot["watered_today"]:
            return False, "Already watered today."
        if self.coins < data.WATER_COST:
            return False, "Not enough coins to water."
        self.coins -= data.WATER_COST
        plot["watered_today"] = True
        return True, "Watered " + plot["crop"] + "."

    def water_all(self):
        count = 0
        for cell in self.all_cells():
            plot = self.plots[cell]
            if plot is not None and not plot["watered_today"] and plot["age"] < plot["grow"]:
                ok, _ = self.water(cell)
                if ok:
                    count += 1
        if count == 0:
            return False, "No plots needed water (or no coins left)."
        return True, "Watered " + str(count) + " plot(s)."

    def rush(self, cell):
        """Pay for fertilizer: the crop instantly grows one extra day."""
        plot = self.plots[cell]
        if self.over:
            return False, "The season is over."
        if plot is None:
            return False, "Nothing planted here."
        if plot["age"] >= plot["grow"]:
            return False, "Already ready to harvest."
        if self.coins < data.RUSH_COST:
            return False, "Fertilizer costs P" + str(data.RUSH_COST) + "."
        self.coins -= data.RUSH_COST
        plot["age"] += 1
        plot["watered_days"] += 1          # fertilized crops count as well cared for
        return True, "Fertilizer! " + plot["crop"] + " grew one day."

    # ------------------------------------------------------------------
    # Harvesting  (INSERTION SORT + RECURSION live here)
    # ------------------------------------------------------------------
    def roll_quality(self, plot):
        ratio = plot["watered_days"] / plot["grow"]
        if ratio >= 0.8:
            odds = data.QUALITY_ODDS["high"]
        elif ratio >= 0.5:
            odds = data.QUALITY_ODDS["mid"]
        else:
            odds = data.QUALITY_ODDS["low"]
        names = list(odds.keys())
        weights = [odds[name] for name in names]
        return self.rng.choices(names, weights=weights)[0]

    def harvest(self, cell):
        if self.over:
            return False, "The season is over."
        plot = self.plots[cell]
        if plot is None:
            return False, "Nothing planted here."
        if not self.is_ready(cell):
            return False, plot["crop"] + " needs " + str(self.remaining(cell)) + " more day(s)."
        if len(self.bodega) >= self.capacity():
            return False, "The Bodega is full! Sell some crates first."

        quality = self.roll_quality(plot)
        crop_name = plot["crop"]
        worth = round(data.CROPS[crop_name]["price"] * data.QUALITY[quality])
        crate = {"crop": crop_name, "quality": quality, "worth": worth}

        # INSERTION SORT: slide the new crate into the ordered Bodega (highest worth first)
        self.lab["insertion"] = ["Bodega before: " + str(len(self.bodega)) + " crate(s)"]
        algorithms.insertion_insert(self.bodega, crate, key=lambda c: c["worth"], reverse=True,
                                    show=lambda c: c["quality"] + " " + c["crop"] + " (worth " + str(c["worth"]) + ")",
                                    log=self.lab["insertion"])
        self.lab["insertion"].append("Bodega now: " + "  ".join(
            str(c["worth"]) for c in self.bodega))

        self.plots[cell] = None
        self.stats["harvested"] += 1
        self.say("Harvested " + quality + " " + crop_name + "!")
        self.unlock("First Harvest")
        if quality == "Premium":
            self.unlock("Premium Pick")
        self.discover(crop_name)
        return True, "Harvested " + quality + " " + crop_name + " (worth P" + str(worth) + ")."

    def harvest_zone(self, node):
        """Harvest every ready plot inside a zone, however deeply nested.

        RECURSION: zones.collect_cells() calls itself on the field, then on each bed,
        until it reaches beds with no children (the base case).
        """
        cells = zones.collect_cells(node, self.is_ready)
        if not cells:
            return False, "Nothing is ready in " + node["name"] + "."
        done = 0
        for cell in cells:
            ok, message = self.harvest(cell)
            if not ok:
                if done == 0:
                    return False, message
                return True, "Harvested " + str(done) + " crop(s) - then " + message
            done += 1
        return True, "Harvested " + str(done) + " crop(s) from " + node["name"] + "."

    def harvest_all(self):
        return self.harvest_zone(self.tree)

    def ready_count(self, node=None):
        node = node or self.tree
        return len(zones.collect_cells(node, self.is_ready))

    def ready_value(self, node=None):
        """Total sell value of everything ready to harvest in a zone (RECURSION)."""
        node = node or self.tree

        def worth(cell):
            if not self.is_ready(cell):
                return 0
            return self.price_of(self.plots[cell]["crop"])

        return zones.sum_values(node, worth)

    # ------------------------------------------------------------------
    # Selling
    # ------------------------------------------------------------------
    def sell_crate(self, position):
        if self.over:
            return False, "The season is over."
        if position < 0 or position >= len(self.bodega):
            return False, "No crate selected."
        crate = self.bodega.pop(position)
        price = self.price_of(crate["crop"], crate["quality"])
        self.coins += price
        self.stats["sold"] += 1
        self.stats["earned"] += price
        self.index[crate["crop"]] = max(data.MIN_INDEX, self.index[crate["crop"]] - data.SALE_DROP)
        self.check_win()
        return True, "Sold " + crate["quality"] + " " + crate["crop"] + " for P" + str(price) + "."

    def sell_best(self):
        """Sell the crate that pays the MOST right now.

        SELECTION SORT step: scan the Bodega and select the largest remaining price.
        (The Bodega is ordered by base worth, but prices change daily, so we still scan.)
        """
        if not self.bodega:
            return False, "The Bodega is empty."
        self.lab["selection"] = ["Looking for the crate with the highest price today..."]
        best = algorithms.selection_pick(
            self.bodega, key=lambda c: self.price_of(c["crop"], c["quality"]), largest=True,
            show=lambda c: c["crop"] + "=" + str(self.price_of(c["crop"], c["quality"])),
            log=self.lab["selection"])
        return self.sell_crate(best)

    def sell_all(self):
        if self.over:
            return False, "The season is over."
        if not self.bodega:
            return False, "The Bodega is empty."
        total = 0
        count = 0
        while self.bodega and not self.over:
            before = self.coins
            ok, _ = self.sell_crate(0)
            if not ok:
                break
            total += self.coins - before
            count += 1
        if total >= 500:
            self.unlock("Big Sale")
        return True, "Sold " + str(count) + " crate(s) for P" + str(total) + "!"

    def check_win(self):
        if not self.over and self.coins >= self.goal:
            self.over = True
            self.won = True
            self.say("You reached the goal! The barangay celebrates!")

    # ------------------------------------------------------------------
    # Ranking and finding  (BUBBLE SORT + SELECTION SORT)
    # ------------------------------------------------------------------
    def market_ranking(self):
        """Rank the discovered crops by today's selling price, best first.

        BUBBLE SORT: repeated adjacent comparisons (see algorithms.bubble_sort).
        Each item is a TUPLE: (crop name, price today).
        """
        items = []
        for name in data.CROPS:
            if name in self.discovered:
                items.append((name, self.price_of(name)))
        self.lab["bubble"] = []
        return algorithms.bubble_sort(items, key=lambda pair: pair[1], reverse=True,
                                      show=lambda pair: pair[0] + ":" + str(pair[1]),
                                      log=self.lab["bubble"])

    def soonest_plot(self):
        """Find the growing crop with the LEAST growth time left.

        SELECTION SORT step: select the smallest remaining value. Returns
        (cell, days_left) as a tuple, or None when nothing is still growing.
        """
        growing = []
        for cell in self.all_cells():
            left = self.remaining(cell)
            if left is not None and left > 0:
                growing.append((cell, left))
        if not growing:
            return None
        self.lab["selection"] = ["Growing crops: " + str(len(growing)),
                                 "Selecting the smallest days-left..."]
        best = algorithms.selection_pick(
            growing, key=lambda pair: pair[1], largest=False,
            show=lambda pair: self.plots[pair[0]]["crop"] + " " + str(pair[1]) + "d",
            log=self.lab["selection"])
        return growing[best]

    # ------------------------------------------------------------------
    # Shopping
    # ------------------------------------------------------------------
    def buy_field(self, index):
        if self.over:
            return False, "The season is over."
        if index in self.owned_fields:
            return False, "You already own this field."
        field = data.FIELDS[index]
        if self.coins < field["cost"]:
            return False, "You need P" + str(field["cost"]) + " for " + field["name"] + "."
        self.coins -= field["cost"]
        self.owned_fields.add(index)
        self.say("You bought the " + field["name"] + "!")
        if len(self.owned_fields) == len(data.FIELDS):
            self.unlock("Land Baron")
        return True, "Bought " + field["name"] + "!"

    def buy_upgrade(self, name):
        if self.over:
            return False, "The season is over."
        if name in self.upgrades:
            return False, "You already have " + name + "."
        cost = data.UPGRADES[name]["cost"]
        if self.coins < cost:
            return False, name + " costs P" + str(cost) + "."
        self.coins -= cost
        self.upgrades.add(name)
        if name == "Irrigation":
            for plot in self.plots.values():
                if plot is not None:
                    plot["grow"] = max(plot["age"], max(2, plot["grow"] - 1))
        self.say("Upgrade bought: " + name + ".")
        return True, "Upgrade bought: " + name + "!"

    def undiscovered(self):
        return [name for name in data.CROPS if name not in self.discovered]

    def buy_packet(self):
        """A Mystery Seed Packet discovers a random new crop (adds to the discovered SET)."""
        if self.over:
            return False, "The season is over."
        choices = self.undiscovered()
        if not choices:
            return False, "You have discovered every crop!"
        if self.coins < data.MYSTERY_PACKET_COST:
            return False, "A packet costs P" + str(data.MYSTERY_PACKET_COST) + "."
        self.coins -= data.MYSTERY_PACKET_COST
        crop_name = self.rng.choice(choices)
        self.discover(crop_name)
        return True, "The packet held " + crop_name + " seeds!"

    # ------------------------------------------------------------------
    # Ending the day  (market moves, plants grow, random events)
    # ------------------------------------------------------------------
    def end_day(self):
        if self.over:
            return False, "The season is over."

        # 1) plants grow
        for plot in self.plots.values():
            if plot is not None and plot["age"] < plot["grow"]:
                plot["age"] += 1
                if plot["watered_today"]:
                    plot["watered_days"] += 1
            if plot is not None:
                plot["watered_today"] = False

        # 2) season over?
        if self.day >= data.TOTAL_DAYS:
            self.over = True
            self.won = self.coins >= self.goal
            self.say("The season has ended.")
            return True, "The season has ended."

        # 3) a new day begins: prices drift back toward normal, with some luck
        self.day += 1
        for name in self.index:
            value = self.index[name]
            value += (1.0 - value) * 0.15 + self.rng.uniform(-0.07, 0.07)
            self.index[name] = min(data.MAX_INDEX, max(data.MIN_INDEX, value))

        # 4) maybe a random event
        self.today_event = None
        if self.events_on and self.rng.random() < data.EVENT_CHANCE:
            self.run_event(self.pick_event())
        if self.is_fiesta():
            extra = (" " + self.today_event[1]) if self.today_event else ""
            self.today_event = ("fiesta", "Fiesta! Sell prices +50%." + extra)
            self.say("Barangay Fiesta! Everything sells for 50% more today.")
        return True, "Day " + str(self.day) + " begins."

    def pick_event(self):
        """Weighted random choice using the EVENTS dictionary."""
        total = sum(info["weight"] for info in data.EVENTS.values())
        roll = self.rng.uniform(0, total)
        running = 0
        for name, info in data.EVENTS.items():
            running += info["weight"]
            if roll <= running:
                return name
        return "rain"

    def planted_cells(self):
        return [cell for cell in self.all_cells() if self.plots[cell] is not None]

    def run_event(self, name):
        text = ""
        if name == "rain":
            for cell in self.planted_cells():
                self.plots[cell]["watered_today"] = True
            text = "Rain! All your plants were watered for free."
        elif name == "typhoon":
            planted = self.planted_cells()
            if "Storm Shield" in self.upgrades:
                text = "A typhoon hit, but your bamboo windbreaks held. No damage!"
                if planted:
                    self.unlock("Storm Survivor")
            else:
                lost = 0
                for cell in planted:
                    if self.rng.random() < 0.35:
                        self.plots[cell] = None
                        lost += 1
                self.stats["lost"] += lost
                text = "Typhoon! You lost " + str(lost) + " plant(s)."
                if planted and lost == 0:
                    self.unlock("Storm Survivor")
        elif name == "pests":
            planted = self.planted_cells()
            if "Scarecrow" in self.upgrades:
                text = "Pests came, but Kuya Berto's scarecrow chased them away!"
            elif planted:
                for _ in range(min(2, len(planted))):
                    cell = self.rng.choice(planted)
                    planted.remove(cell)
                    self.plots[cell] = None
                    self.stats["lost"] += 1
                text = "Pests ate some of your crops!"
            else:
                text = "Pests wandered by, but you had nothing planted."
        elif name == "glut":
            crop = self.rng.choice(list(data.CROPS))
            self.index[crop] = max(data.MIN_INDEX, self.index[crop] * 0.7)
            text = "Too much " + crop + " at the market. Its price fell!"
        elif name == "demand":
            crop = self.rng.choice(list(data.CROPS))
            self.index[crop] = min(data.MAX_INDEX, self.index[crop] * 1.5)
            text = "Everyone wants " + crop + " today! Its price jumped!"
        elif name == "gift":
            amount = self.rng.randint(20, 60)
            self.coins += amount
            text = "The mayor gave you P" + str(amount) + " in ayuda!"
        elif name == "seedswap":
            choices = self.undiscovered()
            if choices:
                crop = self.rng.choice(choices)
                self.discover(crop)
                text = "A neighbour swapped seeds with you: " + crop + "!"
            else:
                self.coins += 30
                text = "A neighbour gave you P30 for your trouble."
        self.today_event = (name, text)
        self.say(text)

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------
    def rank(self):
        title = data.RANKS[0][1]
        for minimum, name in data.RANKS:
            if self.coins >= minimum * self.goal:
                title = name
        return title
