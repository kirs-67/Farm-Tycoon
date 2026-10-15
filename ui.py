"""The Tkinter interface for Bukid Tycoon: picture-based, with sound.

This file only DRAWS the game and sends the player's clicks to game.FarmGame.
The rules, sorting and recursion live in game.py / algorithms.py / zones.py.
The pictures come from icons.py and the sounds from sounds.py.

How the screen works
    * Four canvases are redrawn about 10 times a second: top bar (hud), farm, side panel, bottom dock.
    * Every clickable picture registers a "hit box" with add_hit(); a click finds the box under the mouse.
    * Animation uses Tkinter's timer root.after(). That is the normal event loop and NOT recursion;
      the recursion in this project is only in zones.py.
"""

import math
import tkinter as tk

import data
import icons
import sounds
import zones
from game import FarmGame

# ---- Window layout -----------------------------------------------------------
PAD = 8
WIN_W = 1000
HUD_W = WIN_W - 2 * PAD
HUD_H = 56
FARM_W = 540
SCENE_H = 438
STRIP_H = 30
FARM_H = SCENE_H + STRIP_H
PANEL_W = HUD_W - FARM_W - PAD
DOCK_H = 108
WIN_H = PAD + HUD_H + 4 + FARM_H + 4 + DOCK_H + PAD

# ---- Farm drawing numbers ----------------------------------------------------
CELL = 66
GAP = 5
FIELD_GAP = 14
BED_GAP = 10
MARGIN = 14
GRID_TOP = 134

INK = "#3b2a1a"
PANEL = "#fff3d6"
CARD = "#fff9ea"
GOOD = "#2e7d32"
BAD = "#c62828"
BAR_BG = "#244a29"

TABS = (("market", icons.chart, "Market: crops ranked by price"),
        ("bodega", icons.crate, "Bodega: your crates (click one to sell it)"),
        ("shop", icons.stall, "Shop: land, upgrades and seed packets"),
        ("journal", icons.book, "Journal: crops found and medals"),
        ("lab", icons.flask, "Algo Lab: watch the sorting and recursion (for the teacher)"))

SOUND_FOR = {"plant": "plant", "water": "water", "water_all": "water", "harvest": "harvest",
             "harvest_zone": "harvest", "harvest_all": "harvest", "sell_crate": "sell", "sell_best": "sell",
             "sell_all": "sell", "buy_field": "buy", "buy_upgrade": "buy", "buy_packet": "discover",
             "rush": "boost"}
EVENT_SOUND = {"rain": "rain", "typhoon": "thunder", "pests": "pests", "glut": "down", "demand": "gift",
               "gift": "gift", "seedswap": "discover", "fiesta": "fiesta"}
STARS = {"Normal": 1, "Fine": 2, "Premium": 3}


def cell_box(cell):
    """Pixel rectangle (x1, y1, x2, y2) of a plot. cell is a (row, col) TUPLE."""
    row, col = cell
    field = zones.field_of(cell)
    x = MARGIN + col * (CELL + GAP) + field * FIELD_GAP
    y = GRID_TOP + row * (CELL + GAP) + (BED_GAP if row >= 2 else 0)
    return x, y, x + CELL, y + CELL


def lerp(a, b, t):
    return a + (b - a) * t


def blend(c1, c2, t):
    """Mix two (r, g, b) tuples into a '#rrggbb' colour."""
    return "#%02x%02x%02x" % (int(lerp(c1[0], c2[0], t)), int(lerp(c1[1], c2[1], t)), int(lerp(c1[2], c2[2], t)))


def hex_to_rgb(color):
    return int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)


def label(c, x, y, text, size=10, color=INK, anchor="center", bold=True):
    return c.create_text(x, y, text=text, fill=color, anchor=anchor, font=icons.font(size, bold))


class BukidApp:
    def __init__(self, root, sound=None):
        self.root = root
        self.game = FarmGame()
        self.sound = sound if sound is not None else sounds.SoundBoard()
        self.crop = "Mais"
        self.boost_mode = False
        self.tab = "market"
        self.mode = "menu"            # menu / play / help / end
        self.help_from = "menu"
        self.difficulty = "Normal"
        self.hint = ""
        self.hover = None
        self.highlight = None
        self.last_drag = None
        self.floaters = []
        self.particles = []
        self.confetti = []
        self.banner = None
        self.toast_text = ""
        self.toast_ok = True
        self.toast_life = 0
        self.coin_pulse = 0
        self.tick = 0
        self.ranking = []
        self.farm_buttons = []
        self.hits = {"hud": [], "panel": [], "dock": [], "overlay": []}

        root.title(data.GAME_TITLE)
        root.configure(bg=data.DARK)
        root.geometry(str(WIN_W) + "x" + str(WIN_H))
        root.resizable(False, False)
        self.build_widgets()
        self.show_menu()
        self.refresh()
        self.animate()

    # ==================================================================
    # Widgets
    # ==================================================================
    def build_widgets(self):
        root = self.root
        self.hud = tk.Canvas(root, width=HUD_W, height=HUD_H, bg=data.DARK, highlightthickness=0)
        self.hud.pack(padx=PAD, pady=(PAD, 4))
        middle = tk.Frame(root, bg=data.DARK)
        middle.pack(padx=PAD)
        self.farm = tk.Canvas(middle, width=FARM_W, height=FARM_H, bg="#9bd36b", highlightthickness=0)
        self.farm.pack(side="left")
        self.panel = tk.Canvas(middle, width=PANEL_W, height=FARM_H, bg=PANEL, highlightthickness=0)
        self.panel.pack(side="left", padx=(PAD, 0))
        self.dock = tk.Canvas(root, width=HUD_W, height=DOCK_H, bg=data.DARK, highlightthickness=0)
        self.dock.pack(padx=PAD, pady=(4, PAD))
        self.overlay = tk.Canvas(root, width=WIN_W, height=WIN_H, bg=data.DARK, highlightthickness=0)

        self.lab_text = tk.Text(self.panel, wrap="word", font=("Courier", 9), bg="#1e2a1f", fg="#d6f5d6",
                                relief="flat", padx=8, pady=6)
        self.lab_text.tag_configure("head", foreground=data.GOLD, font=("Courier", 9, "bold"))
        self.lab_text.tag_configure("dim", foreground="#8fb58f")

        for name, canvas in (("hud", self.hud), ("panel", self.panel), ("dock", self.dock), ("overlay", self.overlay)):
            canvas.bind("<Button-1>", lambda event, n=name: self.on_surface_click(n, event))
            canvas.bind("<Motion>", lambda event, n=name: self.on_surface_motion(n, event))
            canvas.bind("<Leave>", self.on_leave)
        self.farm.bind("<Button-1>", self.on_farm_click)
        self.farm.bind("<B1-Motion>", self.on_farm_drag)
        self.farm.bind("<Motion>", self.on_farm_motion)
        self.farm.bind("<Leave>", self.on_leave)
        root.bind("<Key>", self.on_key)

    # ---- Hit boxes -----------------------------------------------------
    def add_hit(self, surface, box, callback, hint="", hid=""):
        self.hits[surface].append({"box": box, "cb": callback, "hint": hint, "id": hid})

    def hit_at(self, surface, x, y):
        for hit in reversed(self.hits[surface]):
            x1, y1, x2, y2 = hit["box"]
            if x1 <= x <= x2 and y1 <= y <= y2:
                return hit
        return None

    def find_hit(self, surface, hid):
        for hit in self.hits[surface]:
            if hit["id"] == hid:
                return hit
        return None

    def on_surface_click(self, surface, event):
        hit = self.hit_at(surface, event.x, event.y)
        if hit is not None and hit["cb"] is not None:
            hit["cb"]()

    def on_surface_motion(self, surface, event):
        hit = self.hit_at(surface, event.x, event.y)
        self.hover = None
        self.hint = hit["hint"] if hit else ""

    def on_leave(self, event):
        self.hover = None
        self.hint = ""

    # ==================================================================
    # Screens: menu, help, end
    # ==================================================================
    def show_overlay(self):
        self.overlay.place(x=0, y=0)

    def show_menu(self):
        self.mode = "menu"
        self.lab_text.place_forget()
        self.show_overlay()

    def start_game(self):
        self.game.set_difficulty(self.difficulty)
        self.mode = "play"
        self.overlay.place_forget()
        self.floaters = []
        self.particles = []
        self.confetti = []
        self.highlight = None
        self.boost_mode = False
        self.crop = "Mais"
        self.banner = {"text": "Day 1", "life": 16}
        self.toast("Pick a seed below, then click your plots!")
        self.sound.play("day")
        self.set_tab("market", quiet=True)
        self.refresh()

    def restart(self):
        self.start_game()

    def show_help(self):
        if self.mode == "help":
            return
        self.help_from = self.mode
        self.mode = "help"
        self.show_overlay()
        self.sound.play("click")

    def close_help(self):
        self.mode = self.help_from
        if self.mode == "play":
            self.overlay.place_forget()
        self.sound.play("click")

    def show_end(self):
        game = self.game
        if not game.over or self.mode == "end":
            return
        self.mode = "end"
        self.lab_text.place_forget()
        self.show_overlay()
        self.confetti = []
        if game.won:
            colors = ("#e53935", "#fdd835", "#43a047", "#1e88e5", "#ec407a")
            for i in range(60):
                self.confetti.append({"x": (i * 83) % WIN_W, "y": -((i * 47) % 400), "vy": 2 + (i % 5),
                                      "color": colors[i % len(colors)]})
        self.sound.play("win" if game.won else "lose")

    # ==================================================================
    # Keyboard
    # ==================================================================
    def on_key(self, event):
        key = event.keysym.lower()
        if key == "m":
            self.toggle_sound()
            return
        if self.mode == "help":
            self.close_help()
            return
        if key in ("question", "slash", "f1"):
            self.show_help()
            return
        if self.mode == "menu":
            if key in ("return", "space"):
                self.start_game()
            return
        if self.mode != "play":
            return
        if key == "escape":
            self.show_menu()
        elif key == "space":
            self.end_day()
        elif key == "a":
            self.water_all()
        elif key == "h":
            self.harvest_all()
        elif key == "s":
            self.sell_best()
        elif key == "n":
            self.next_up()
        elif key == "b":
            self.toggle_boost()
        elif key in "12345678" and len(key) == 1:
            name = list(data.CROPS)[int(key) - 1]
            if name in self.game.discovered:
                self.select_seed(name)

    # ==================================================================
    # Player actions
    # ==================================================================
    def toast(self, text, ok=True):
        self.toast_text = text
        self.toast_ok = ok
        self.toast_life = 38

    def run(self, func, *args, sound=None, at=None, quiet=False):
        """Run a game action, then show sound, message, coin sparkles and the ending if any."""
        game = self.game
        coins_before = game.coins
        achievements_before = len(game.achievements)
        found_before = len(game.discovered)
        result = func(*args)
        if len(result) == 3:
            ok, message, kind = result
        else:
            (ok, message), kind = result, None
        name = sound or SOUND_FOR.get(kind or func.__name__)
        if ok:
            if not quiet:
                self.toast(message, True)
            if name:
                self.sound.play(name)
        elif kind == "info":
            if not quiet:
                self.toast(message, True)
        elif not quiet:
            self.toast(message, False)
            self.sound.play("error")

        gained = game.coins - coins_before
        if gained > 0:
            self.coin_pulse = 8
            where = at or (155, 90)
            self.burst(where[0], where[1], "coin", 8)
            self.floaters.append({"x": where[0], "y": where[1] - 12, "text": "+P" + str(gained),
                                  "color": "#1b5e20", "life": 26})
        if len(game.achievements) > achievements_before:
            self.root.after(350, lambda: self.sound.play("achieve"))
            self.banner = {"text": "New medal!", "life": 18}
        elif len(game.discovered) > found_before and name != "discover":
            self.root.after(350, lambda: self.sound.play("discover"))
        self.highlight = None
        self.refresh()
        if game.over and self.mode == "play":
            self.root.after(600, self.show_end)
        return ok

    def burst(self, x, y, kind, count):
        for i in range(count):
            angle = (i / count) * 2 * math.pi + self.tick
            speed = 1.5 + (i % 3)
            self.particles.append({"x": x, "y": y, "vx": math.cos(angle) * speed, "vy": math.sin(angle) * speed - 2,
                                   "kind": kind, "life": 16 + (i % 5)})

    def water_all(self):
        self.run(self.game.water_all)

    def harvest_all(self):
        self.run(self.game.harvest_all)

    def sell_all(self):
        self.run(self.game.sell_all)

    def sell_best(self):
        self.run(self.game.sell_best)

    def end_day(self):
        if self.mode != "play":
            return
        ok = self.run(self.game.end_day)
        if ok and not self.game.over:
            self.banner = {"text": "Day " + str(self.game.day), "life": 14}
            event = self.game.today_event
            self.sound.play(EVENT_SOUND.get(event[0], "day") if event else "day")
            if event:
                self.toast(event[1], True)

    def next_up(self):
        found = self.game.soonest_plot()          # SELECTION SORT step
        self.refresh_lab()
        if found is None:
            self.toast("Nothing is growing yet. Plant something!", False)
            self.sound.play("error")
            return
        cell, left = found
        self.highlight = cell
        self.sound.play("click")
        self.toast(self.game.plots[cell]["crop"] + " finishes first: " + str(left) + " day(s) to go.")
        self.draw_all()

    def toggle_boost(self):
        self.boost_mode = not self.boost_mode
        self.sound.play("boost" if self.boost_mode else "click")
        if self.boost_mode:
            self.toast("Boost on: click a growing crop to grow it 1 day (P" + str(data.RUSH_COST) + ").")
        else:
            self.toast("Boost off.")
        self.draw_all()

    def toggle_sound(self):
        on = self.sound.toggle()
        self.toast("Sound on." if on else "Sound off.")

    def select_seed(self, name):
        self.crop = name
        self.boost_mode = False
        self.sound.play("click")
        self.toast(name + ": " + data.CROPS[name]["blurb"])
        self.draw_all()

    def set_tab(self, name, quiet=False):
        self.tab = name
        if not quiet:
            self.sound.play("click")
        if name == "lab" and self.mode == "play":
            self.lab_text.place(x=8, y=56, width=PANEL_W - 16, height=FARM_H - 64)
            self.refresh_lab()
        else:
            self.lab_text.place_forget()
        self.draw_all()

    # ---- Mouse on the farm ----------------------------------------------
    def cell_at(self, px, py):
        for cell in self.game.all_cells():
            x1, y1, x2, y2 = cell_box(cell)
            if x1 <= px <= x2 and y1 <= py <= y2:
                return cell
        return None

    def on_farm_motion(self, event):
        self.hover = self.cell_at(event.x, event.y)
        self.hint = ""
        for box, callback, hint in self.farm_buttons:
            if box[0] <= event.x <= box[2] and box[1] <= event.y <= box[3]:
                self.hint = hint
                return
        if self.hover is not None:
            self.hint = self.plot_hint(self.hover)

    def plot_hint(self, cell):
        game = self.game
        plot = game.plots[cell]
        if not game.is_unlocked(cell):
            return "Locked field. Click the padlock to buy it."
        if plot is None:
            return "Empty plot: click to plant " + self.crop + "."
        if game.is_ready(cell):
            return plot["crop"] + " is ready: click to harvest!"
        left = game.remaining(cell)
        thirsty = "" if plot["watered_today"] else " Click to water."
        return plot["crop"] + ": " + str(left) + " day(s) left." + thirsty

    def on_farm_click(self, event):
        if self.mode != "play" or self.game.over:
            return
        for box, callback, hint in self.farm_buttons:
            if box[0] <= event.x <= box[2] and box[1] <= event.y <= box[3]:
                callback()
                return
        cell = self.cell_at(event.x, event.y)
        self.last_drag = cell
        if cell is not None:
            self.click_plot(cell, quiet=False)

    def on_farm_drag(self, event):
        """Hold the mouse button and drag across plots to plant, water or harvest many at once."""
        if self.mode != "play" or self.game.over:
            return
        cell = self.cell_at(event.x, event.y)
        if cell is not None and cell != self.last_drag:
            self.last_drag = cell
            self.click_plot(cell, quiet=True)

    def click_plot(self, cell, quiet=False):
        game = self.game
        x1, y1, x2, y2 = cell_box(cell)
        centre = ((x1 + x2) / 2, (y1 + y2) / 2)
        if not game.is_unlocked(cell):
            if not quiet:
                self.toast("Locked! Click the padlock to buy this field.", False)
                self.sound.play("error")
            return
        if self.boost_mode:
            ok = self.run(game.rush, cell, at=centre, quiet=quiet)
            kind = "boost"
        else:
            coins = game.coins
            ok = self.run(game.smart_action, cell, self.crop, at=centre, quiet=quiet)
            kind = "plant" if game.coins < coins and ok else "other"
        if ok:
            self.burst(centre[0], centre[1], "dirt" if kind == "plant" else "spark", 6)

    def buy_field_action(self, index):
        self.run(self.game.buy_field, index)

    def harvest_field_action(self, index):
        self.run(self.game.harvest_zone, self.game.tree["children"][index])     # RECURSION

    # ==================================================================
    # Refresh and animation
    # ==================================================================
    def refresh(self):
        game = self.game
        self.ranking = game.market_ranking()          # BUBBLE SORT runs here
        if self.crop not in game.discovered:
            self.crop = "Mais"
        if self.tab == "lab":
            self.refresh_lab()
        self.draw_all()

    def animate(self):
        self.tick += 1
        if self.toast_life > 0:
            self.toast_life -= 1
        if self.coin_pulse > 0:
            self.coin_pulse -= 1
        self.draw_all()
        self.root.after(100, self.animate)

    def draw_all(self):
        self.draw_hud()
        self.draw_farm()
        self.draw_panel()
        self.draw_dock()
        if self.mode != "play":
            self.draw_overlay()

    def weather(self):
        event = self.game.today_event
        if event is None:
            return None
        if event[0] == "fiesta":
            return "rain" if "Rain!" in event[1] else "fiesta"
        return event[0]

    # ==================================================================
    # Top bar
    # ==================================================================
    def draw_hud(self):
        c = self.hud
        game = self.game
        c.delete("all")
        self.hits["hud"] = []
        icons.rrect(c, 0, 0, HUD_W, HUD_H, 14, fill=BAR_BG, outline="")
        icons.barn(c, 30, 30, 0.8)
        label(c, 56, 28, "BUKID TYCOON", 14, data.GOLD, "w")

        # day: sun + number + a bar with a flag on every fiesta day
        icons.sun(c, 262, 22, 0.8, self.tick)
        label(c, 282, 20, str(game.day), 18, "white", "w")
        label(c, 282 + 10 * len(str(game.day)) + 12, 24, "/" + str(data.TOTAL_DAYS), 10, "#a8c8a8", "w")
        bx1, bx2 = 242, 412
        icons.rrect(c, bx1, 42, bx2, 50, 4, fill="#1a3a1e", outline="")
        icons.rrect(c, bx1, 42, bx1 + max(8, (bx2 - bx1) * game.day / data.TOTAL_DAYS), 50, 4, fill="#7fd1ff", outline="")
        for day in data.FIESTA_DAYS:
            icons.flag(c, bx1 + (bx2 - bx1) * day / data.TOTAL_DAYS - 1, 38, 0.38, "#ffb300" if game.day >= day else "#e57373")
        self.add_hit("hud", (236, 6, 420, 54), None, "Day " + str(game.day) + " of " + str(data.TOTAL_DAYS) + ". Flags are Fiesta days (+50% prices).")

        # coins and goal
        pulse = 1.0 + 0.04 * self.coin_pulse
        icons.coin(c, 462, 20, pulse)
        label(c, 482, 20, str(game.coins), 18, data.GOLD, "w")
        gx1, gx2 = 442, 640
        icons.rrect(c, gx1, 42, gx2, 50, 4, fill="#1a3a1e", outline="")
        share = min(1.0, game.coins / game.goal)
        icons.rrect(c, gx1, 42, gx1 + max(8, (gx2 - gx1) * share), 50, 4, fill=data.GOLD, outline="")
        icons.trophy(c, 662, 28, 0.55)
        label(c, 680, 30, str(game.goal), 11, "#fff3d6", "w")
        self.add_hit("hud", (436, 6, 740, 54), None, "Coins " + str(game.coins) + ". Goal: " + str(game.goal) + " before Day " + str(data.TOTAL_DAYS) + ".")

        # today's event
        event = game.today_event
        c.create_oval(758, 8, 794, 48, fill="#2f5d34", outline=data.GOLD, width=2)
        icons.event_icon(c, 776, 28, 0.85, event[0] if event else None, self.tick)
        self.add_hit("hud", (758, 8, 794, 48), None, event[1] if event else "A quiet day on the farm.")

        # buttons
        for x, hid, hint, callback, draw in (
                (828, "sound", "Sound on or off (M)", self.toggle_sound, lambda x: icons.speaker(c, x, 28, 0.8, self.sound.enabled and self.sound.available)),
                (868, "help", "How to play (?)", self.show_help, lambda x: icons.help_icon(c, x, 28, 0.8)),
                (908, "menu", "Main menu (Esc)", self.show_menu, lambda x: icons.home(c, x, 28, 0.8)),
                (948, "restart", "Restart this game", self.restart, lambda x: icons.restart(c, x, 28, 0.8))):
            c.create_oval(x - 17, 11, x + 17, 45, fill="#4b7f52", outline="")
            draw(x)
            self.add_hit("hud", (x - 17, 11, x + 17, 45), callback, hint, hid)

    # ==================================================================
    # The farm
    # ==================================================================
    def draw_farm(self):
        c = self.farm
        game = self.game
        c.delete("all")
        self.farm_buttons = []
        weather = self.weather()
        progress = (game.day - 1) / max(1, data.TOTAL_DAYS - 1)
        self.draw_sky(c, FARM_W, weather, progress)
        self.draw_bahay_kubo(c)
        self.draw_bodega_icon(c)
        if "Scarecrow" in game.upgrades:
            icons.scarecrow(c, 520, 122)
        if game.is_fiesta():
            self.draw_bunting(c)

        # soil behind each field, canals when Irrigation is owned
        grid_bottom = cell_box((3, 0))[3]
        for index, field in enumerate(data.FIELDS):
            first_col, last_col = field["cols"]
            x1 = cell_box((0, first_col))[0] - 5
            x2 = cell_box((0, last_col))[2] + 5
            c.create_rectangle(x1, GRID_TOP - 6, x2, grid_bottom + 5,
                               fill="#7a5230" if index in game.owned_fields else "#9a9484", outline="#4a3018", width=2)
        if "Irrigation" in game.upgrades:
            for index in range(len(data.FIELDS) - 1):
                x = cell_box((0, data.FIELDS[index]["cols"][1]))[2] + 8
                c.create_rectangle(x, GRID_TOP - 6, x + 6, grid_bottom + 5, fill="#4fc3f7", outline="")
                wave = (self.tick * 3) % 40
                for k in range(0, 330, 40):
                    c.create_line(x + 3, GRID_TOP + k + wave - 40, x + 3, GRID_TOP + k + wave - 30, fill="#e1f5fe", width=2)
        if "Storm Shield" in game.upgrades:
            for x in range(6, FARM_W, 14):
                c.create_line(x, SCENE_H - 12, x, SCENE_H - 2, fill="#8d6e3f", width=5)
            c.create_line(0, SCENE_H - 9, FARM_W, SCENE_H - 9, fill="#c9a769", width=2)

        for cell in game.all_cells():
            self.draw_plot(c, cell)
        self.draw_field_headers(c)
        self.draw_weather(c, weather)
        self.draw_particles(c)
        self.draw_strip(c)
        if self.banner:
            c.create_rectangle(120, 150, 420, 210, fill=data.DARK, outline=data.GOLD, width=3)
            icons.sun(c, 156, 180, 1.0, self.tick)
            label(c, 292, 180, self.banner["text"], 22, data.GOLD)
            self.banner["life"] -= 1
            if self.banner["life"] <= 0:
                self.banner = None

    def draw_sky(self, c, width, weather, progress, sun_x=490):
        top = blend((110, 190, 240), (236, 140, 110), progress)
        low = blend((200, 236, 255), (255, 214, 150), progress)
        if weather == "typhoon":
            top, low = "#5d6b78", "#8795a1"
        elif weather == "rain":
            top, low = "#8fa6b8", "#c2d0da"
        for i in range(11):
            c.create_rectangle(0, i * 11, width, i * 11 + 12, fill=blend(hex_to_rgb(top), hex_to_rgb(low), i / 10), outline="")
        if weather != "typhoon":
            sx, sy = sun_x, 46 + progress * 14
            for k in range(10):
                angle = self.tick * 0.05 + k * math.pi / 5
                c.create_line(sx + math.cos(angle) * 26, sy + math.sin(angle) * 26, sx + math.cos(angle) * 36,
                              sy + math.sin(angle) * 36, fill="#ffd54f", width=3)
            c.create_oval(sx - 22, sy - 22, sx + 22, sy + 22, fill="#ffca28", outline="#ffb300", width=2)
        for base, y, size in ((40, 24, 1.0), (230, 48, 1.3), (390, 16, 0.8)):
            x = (base + self.tick * (0.5 + size * 0.2)) % (width + 140) - 70
            icons.cloud(c, x, y, size * 1.5, "#ffffff" if weather not in ("typhoon", "rain") else "#7d8a96")
        c.create_polygon(0, 112, 0, 84, 90, 62, 190, 82, 300, 58, 420, 80, width, 60, width, 112, fill="#6fb35a", outline="")
        c.create_polygon(0, 112, 0, 98, 120, 84, 250, 100, 380, 88, width, 102, width, 112, fill="#4f9a47", outline="")
        c.create_rectangle(0, 106, width, SCENE_H, fill="#a5d86f", outline="")

    def draw_bahay_kubo(self, c):
        for x in (36, 56, 78, 98):
            c.create_line(x, 100, x, 112, fill="#6d4c2a", width=4)
        c.create_rectangle(30, 88, 104, 98, fill="#a9794a", outline="#5d3d1f", width=2)
        c.create_rectangle(36, 70, 98, 88, fill="#d9b06a", outline="#8a5f2c", width=2)
        for x in range(42, 98, 10):
            c.create_line(x, 70, x, 88, fill="#b98a45")
        c.create_rectangle(60, 74, 76, 88, fill="#5d3d1f", outline="")
        c.create_polygon(24, 72, 67, 40, 110, 72, fill="#e2c15a", outline="#a8812c", width=2)
        c.create_line(24, 72, 110, 72, fill="#a8812c", width=3)

    def draw_bodega_icon(self, c):
        game = self.game
        big = "Bodega" in game.upgrades
        x0 = 130
        width = 64 if big else 48
        c.create_rectangle(x0, 74, x0 + width, 100, fill="#b5651d", outline="#5d3d1f", width=2)
        c.create_polygon(x0 - 4, 76, x0 + width / 2, 54, x0 + width + 4, 76, fill="#c0392b", outline="#7b241c", width=2)
        c.create_rectangle(x0 + 8, 82, x0 + 20, 100, fill="#3e2a14", outline="")
        stack = int(5 * len(game.bodega) / max(1, game.capacity()))
        for k in range(stack):
            c.create_rectangle(x0 + width - 20, 98 - (k + 1) * 6, x0 + width - 6, 98 - k * 6, fill="#f2c66d", outline="#8a5f2c")

    def draw_bunting(self, c):
        colors = ("#e53935", "#fdd835", "#43a047", "#1e88e5", "#8e24aa")
        for k in range(0, FARM_W, 36):
            sag = 6 * math.sin((k / FARM_W) * math.pi * 3)
            c.create_polygon(k, 4 + sag, k + 30, 4 + sag, k + 15, 26 + sag, fill=colors[(k // 36) % len(colors)], outline="")
        c.create_line(0, 4, FARM_W, 4, fill="#5d3d1f", width=2)

    def draw_field_headers(self, c):
        game = self.game
        grid_bottom = cell_box((3, 0))[3]
        for index, field in enumerate(data.FIELDS):
            first_col, last_col = field["cols"]
            x1 = cell_box((0, first_col))[0]
            x2 = cell_box((0, last_col))[2]
            y1, y2 = GRID_TOP - 27, GRID_TOP - 6
            owned = index in game.owned_fields
            icons.rrect(c, x1, y1, x2, y2, 6, fill=data.DARK if owned else "#6b6558", outline=data.GOLD, width=2)
            if owned:
                ready = game.ready_count(game.tree["children"][index])
                label(c, x1 + 10, (y1 + y2) / 2, field["short"], 9, "white", "w")
                icons.basket(c, x2 - 40, (y1 + y2) / 2 - 1, 0.45, produce=False)
                if ready:
                    pulse = 1 if (self.tick // 3) % 2 else 0
                    c.create_oval(x2 - 24 - pulse, y1 + 2 - pulse, x2 - 4 + pulse, y2 - 2 + pulse, fill=data.GOLD, outline="#b8860b")
                    label(c, x2 - 14, (y1 + y2) / 2, str(ready), 9, INK)
                self.farm_buttons.append(((x1, y1, x2, y2), lambda i=index: self.harvest_field_action(i),
                                          "Harvest everything ready in this field."))
            else:
                icons.lock(c, x1 + 12, (y1 + y2) / 2 - 1, 0.45)
                label(c, x1 + 26, (y1 + y2) / 2, field["short"], 9, "#ffe082", "w")
                icons.coin(c, x2 - 36, (y1 + y2) / 2, 0.5)
                label(c, x2 - 28, (y1 + y2) / 2, str(field["cost"]), 8, "#ffe082", "w")
                midx = (x1 + x2) / 2
                midy = (GRID_TOP + grid_bottom) / 2
                c.create_rectangle(x1, y2 + 6, x2, grid_bottom, fill="#2b1d10", outline="", stipple="gray50")
                icons.rrect(c, midx - 46, midy - 38, midx + 46, midy + 38, 12, fill="#3b2a1a", outline=data.GOLD, width=3)
                icons.lock(c, midx, midy - 10, 1.2)
                icons.coin(c, midx - 18, midy + 24, 0.8)
                label(c, midx - 6, midy + 24, str(field["cost"]), 13, data.GOLD, "w")
                affordable = game.coins >= field["cost"]
                if affordable and (self.tick // 3) % 2 == 0:
                    c.create_rectangle(midx - 48, midy - 40, midx + 48, midy + 40, outline="#fff59d", width=2)
                self.farm_buttons.append(((midx - 46, midy - 38, midx + 46, midy + 38),
                                          lambda i=index: self.buy_field_action(i),
                                          "Click to buy this field (8 more plots)."))
                self.farm_buttons.append(((x1, y1, x2, y2), lambda i=index: self.buy_field_action(i),
                                          "Click to buy this field (8 more plots)."))

    def draw_plot(self, c, cell):
        game = self.game
        x1, y1, x2, y2 = cell_box(cell)
        plot = game.plots[cell]
        unlocked = game.is_unlocked(cell)
        soil = "#8b5a35"
        if not unlocked:
            soil = "#a39a8a"
        elif plot is not None and plot["watered_today"]:
            soil = "#5f3b21"
        c.create_rectangle(x1, y1, x2, y2, fill=soil, outline="#4a3018", width=2)
        for k in (1, 2, 3):
            y = y1 + k * CELL / 4
            c.create_line(x1 + 6, y, x2 - 6, y, fill="#6d4524" if unlocked else "#8d8575")
        if unlocked and plot is None:
            if self.hover == cell and not self.boost_mode:
                icons.crop_icon(c, (x1 + x2) / 2, (y1 + y2) / 2 - 2, self.crop, 0.45)
                c.create_rectangle(x1, y1, x2, y2, outline="white", width=3)
            return
        if plot is None:
            return
        cx = (x1 + x2) / 2
        ready = game.is_ready(cell)
        fraction = min(1.0, plot["age"] / plot["grow"])
        icons.draw_crop(c, cx, y2 - 14, plot["crop"], fraction, ready, self.tick, 0.9)
        if ready:
            c.create_rectangle(x1 + 1, y1 + 1, x2 - 1, y2 - 1, outline=data.GOLD, width=3 if (self.tick // 3) % 2 == 0 else 2)
            icons.basket(c, x2 - 14, y1 + 15 + (1 if (self.tick // 3) % 2 else 0), 0.45)
        else:
            count = plot["grow"]
            for i in range(count):                         # one dot per growing day
                px = cx + (i - (count - 1) / 2) * 8
                filled = i < plot["age"]
                c.create_oval(px - 2.6, y2 - 8.6, px + 2.6, y2 - 3.4, fill="#a5f08a" if filled else "", outline="#f5e6c8")
            if plot["watered_today"]:
                icons.drop(c, x1 + 11, y1 + 12, 0.6)
            elif (self.tick // 4) % 2 == 0:
                icons.drop(c, x1 + 11, y1 + 12, 0.6, filled=False, color="#90caf9")
        if self.highlight == cell:
            c.create_rectangle(x1 - 2, y1 - 2, x2 + 2, y2 + 2, outline="#00e5ff", width=3,
                               dash=(5, 3) if (self.tick // 2) % 2 == 0 else (2, 4))
        if self.hover == cell:
            c.create_rectangle(x1, y1, x2, y2, outline="white", width=3)

    def draw_weather(self, c, weather):
        if weather in ("rain", "typhoon"):
            heavy = weather == "typhoon"
            for i in range(70 if heavy else 40):
                x = (i * 53 + self.tick * (14 if heavy else 7)) % (FARM_W + 60) - 30
                y = (i * 97 + self.tick * (26 if heavy else 18)) % SCENE_H
                slant = 14 if heavy else 4
                c.create_line(x, y, x - slant, y + 16, fill="#e3f2fd" if heavy else "#90caf9", width=2 if heavy else 1)
        elif weather == "fiesta":
            colors = ("#e53935", "#fdd835", "#43a047", "#1e88e5", "#ec407a")
            for i in range(26):
                x = (i * 71 + self.tick * 2) % FARM_W
                y = (i * 37 + self.tick * 5) % SCENE_H
                c.create_rectangle(x, y, x + 5, y + 5, fill=colors[i % len(colors)], outline="")
        elif weather == "pests":
            for i in range(8):
                x = (i * 67 + self.tick * 4) % FARM_W
                y = GRID_TOP + (i * 41) % 300 + 6 * math.sin(self.tick * 0.5 + i)
                c.create_oval(x, y, x + 5, y + 4, fill="#212121", outline="")
        elif weather in ("demand", "gift"):
            for i in range(6):
                icons.coin(c, 70 + i * 80, 120 - ((self.tick * 3 + i * 40) % 120) / 2, 0.7)

    def draw_particles(self, c):
        alive = []
        for p in self.particles:
            if p["kind"] == "coin":
                icons.coin(c, p["x"], p["y"], 0.5)
                p["vy"] += 0.35
            elif p["kind"] == "spark":
                c.create_line(p["x"] - 4, p["y"], p["x"] + 4, p["y"], fill="#fff59d", width=2)
                c.create_line(p["x"], p["y"] - 4, p["x"], p["y"] + 4, fill="#fff59d", width=2)
                p["vy"] += 0.1
            else:
                c.create_oval(p["x"] - 2, p["y"] - 2, p["x"] + 2, p["y"] + 2, fill="#6d4524", outline="")
                p["vy"] += 0.3
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"] > 0:
                alive.append(p)
        self.particles = alive
        floating = []
        for item in self.floaters:
            c.create_text(item["x"] + 1, item["y"] + 1, text=item["text"], fill="white", font=icons.font(12))
            c.create_text(item["x"], item["y"], text=item["text"], fill=item["color"], font=icons.font(12))
            item["y"] -= 1.6
            item["life"] -= 1
            if item["life"] > 0:
                floating.append(item)
        self.floaters = floating

    def draw_strip(self, c):
        """The bottom bar of the farm: Kuya Berto shows messages and hints."""
        c.create_rectangle(0, SCENE_H, FARM_W, FARM_H, fill="#2b1d10", outline="")
        icons.farmer(c, 22, SCENE_H + 17, 0.9)
        if self.toast_life > 0:
            text, color = self.toast_text, ("#ffe9a8" if self.toast_ok else "#ff9e8a")
        else:
            text, color = self.hint, "#cdb98a"
        label(c, 44, SCENE_H + 16, text, 10, color, "w")

    # ==================================================================
    # Side panel
    # ==================================================================
    def draw_panel(self):
        c = self.panel
        c.delete("all")
        self.hits["panel"] = []
        c.create_rectangle(0, 0, PANEL_W, FARM_H, fill=PANEL, outline="")
        width = PANEL_W / len(TABS)
        for i, (name, draw, hint) in enumerate(TABS):
            x1, x2 = i * width, (i + 1) * width
            active = name == self.tab
            icons.rrect(c, x1 + 3, 4 if active else 8, x2 - 3, 50, 10, fill=data.GOLD if active else "#e9d9a8", outline="#c9a23a" if active else "")
            draw(c, (x1 + x2) / 2, 29, 0.85 if active else 0.75)
            if name == "bodega" and self.game.bodega:
                c.create_oval(x2 - 24, 8, x2 - 6, 26, fill="#e53935", outline="white")
                label(c, x2 - 15, 17, str(len(self.game.bodega)), 8, "white")
            self.add_hit("panel", (x1, 0, x2, 50), lambda n=name: self.set_tab(n), hint, "tab:" + name)
        c.create_line(0, 52, PANEL_W, 52, fill=data.GOLD, width=3)
        if self.tab == "market":
            self.draw_market(c)
        elif self.tab == "bodega":
            self.draw_bodega(c)
        elif self.tab == "shop":
            self.draw_shop(c)
        elif self.tab == "journal":
            self.draw_journal(c)

    def draw_market(self, c):
        game = self.game
        maxp = max([price for _, price in self.ranking] or [1])
        shown = set()
        medal_colors = ("#ffca28", "#cfd8dc", "#d7966b")
        for i, (name, price) in enumerate(self.ranking):
            shown.add(name)
            top = 60 + i * 46
            selected = name == self.crop
            icons.rrect(c, 10, top, PANEL_W - 10, top + 42, 10, fill="#ffe9a8" if selected else CARD, outline=data.GOLD if selected else "#e6d4a0", width=2)
            c.create_oval(16, top + 8, 42, top + 34, fill=medal_colors[i] if i < 3 else "#e9d9a8", outline="#b8860b")
            label(c, 29, top + 21, str(i + 1), 11)
            icons.crop_icon(c, 74, top + 21, name, 0.5)
            label(c, 100, top + 21, name, 10, INK, "w")
            level = game.index[name]
            color = "#43a047" if level > 1.05 else "#e53935" if level < 0.95 else data.GOLD
            icons.rrect(c, 176, top + 14, 338, top + 28, 6, fill="#efe2b8", outline="")
            icons.rrect(c, 176, top + 14, 176 + max(10, 162 * price / maxp), top + 28, 6, fill=color, outline="")
            label(c, 348, top + 21, "P" + str(price), 12, INK, "w")
            if level > 1.05:
                icons.arrow(c, PANEL_W - 30, top + 21, 1.0, True, GOOD)
            elif level < 0.95:
                icons.arrow(c, PANEL_W - 30, top + 21, 1.0, False, BAD)
            self.add_hit("panel", (10, top, PANEL_W - 10, top + 42), lambda n=name: self.select_seed(n),
                         name + " sells for P" + str(price) + ". Click to pick this seed.", "price:" + name)
        i = len(self.ranking)
        for name in data.CROPS:
            if name in shown:
                continue
            top = 60 + i * 46
            icons.rrect(c, 10, top, PANEL_W - 10, top + 42, 10, fill="#e6dfc8", outline="#d0c6a4", width=2)
            icons.lock(c, 29, top + 21, 0.6, "#b9b29a")
            label(c, 100, top + 21, "???", 10, "#9a8b66", "w")
            self.add_hit("panel", (10, top, PANEL_W - 10, top + 42), None, "Undiscovered. Try a Mystery Seed Packet in the Shop!")
            i += 1
        if game.is_fiesta():
            icons.rrect(c, 10, FARM_H - 42, PANEL_W - 10, FARM_H - 8, 10, fill=data.GOLD, outline="#b8860b", width=2)
            icons.flag(c, 40, FARM_H - 25, 0.9, "#e53935")
            icons.flag(c, 70, FARM_H - 25, 0.9, "#1e88e5")
            label(c, PANEL_W / 2, FARM_H - 25, "FIESTA  x1.5", 14)

    def draw_bodega(self, c):
        game = self.game
        capacity = game.capacity()
        count = len(game.bodega)
        icons.crate(c, 34, 76, 0.9)
        icons.rrect(c, 60, 68, 330, 84, 7, fill="#efe2b8", outline="")
        full = count / capacity
        icons.rrect(c, 60, 68, 60 + max(10, 270 * full), 84, 7, fill="#e53935" if full >= 1 else data.GOLD, outline="")
        label(c, 342, 76, str(count) + "/" + str(capacity), 13, INK, "w")
        self.add_hit("panel", (10, 60, PANEL_W - 10, 92), None, "Bodega: " + str(count) + " of " + str(capacity) + " crates. Best crates are kept first (Insertion Sort).")
        x0, y0, size, step = 17, 100, 62, 68
        for i in range(capacity):
            x = x0 + (i % 6) * step
            y = y0 + (i // 6) * step
            if i < count:
                crate = game.bodega[i]
                icons.rrect(c, x, y, x + size, y + size, 8, fill=data.QUALITY_COLORS[crate["quality"]], outline="#8a5f2c", width=3)
                icons.crop_icon(c, x + 31, y + 27, crate["crop"], 0.5)
                for k in range(STARS[crate["quality"]]):
                    icons.star(c, x + 31 + (k - (STARS[crate["quality"]] - 1) / 2) * 13, y + 53, 5)
                price = game.price_of(crate["crop"], crate["quality"])
                self.add_hit("panel", (x, y, x + size, y + size), lambda n=i: self.run(game.sell_crate, n),
                             crate["quality"] + " " + crate["crop"] + ": click to sell for P" + str(price) + ".", "crate:" + str(i))
            else:
                c.create_rectangle(x, y, x + size, y + size, outline="#c9b98a", dash=(4, 3), width=2)
        rows = (capacity + 5) // 6
        by = y0 + rows * step + 6
        for x, hid, text, callback, hint in ((14, "sell_best", "Sell best", self.sell_best, "Sell the crate that pays most today (S)."),
                                             (222, "sell_all", "Sell all", self.sell_all, "Sell every crate.")):
            icons.rrect(c, x, by, x + 200, by + 54, 12, fill=data.GOLD, outline="#b8860b", width=2)
            icons.coin(c, x + 30, by + 27, 1.2)
            if hid == "sell_best":
                icons.star(c, x + 52, by + 15, 6)
            label(c, x + 120, by + 27, text, 13)
            self.add_hit("panel", (x, by, x + 200, by + 54), callback, hint, hid)

    def shop_cards(self):
        game = self.game
        cards = []
        for index in range(1, len(data.FIELDS)):
            field = data.FIELDS[index]
            cards.append({"id": "field" + str(index), "name": field["short"] + " field", "cost": field["cost"],
                          "owned": index in game.owned_fields, "icon": icons.field_icon,
                          "hint": "Buy the " + field["name"] + ": 8 more plots.",
                          "cb": lambda i=index: self.buy_field_action(i)})
        for name, info in data.UPGRADES.items():
            cards.append({"id": name, "name": name, "cost": info["cost"], "owned": name in game.upgrades,
                          "icon": lambda c, x, y, s, n=name: icons.upgrade_icon(c, x, y, s, n),
                          "hint": info["desc"], "cb": lambda n=name: self.run(game.buy_upgrade, n)})
        left = len(game.undiscovered())
        cards.append({"id": "packet", "name": "Mystery seeds", "cost": data.MYSTERY_PACKET_COST, "owned": left == 0,
                      "icon": icons.packet, "badge": left, "hint": "Discover a random new crop (" + str(left) + " left to find).",
                      "cb": lambda: self.run(game.buy_packet)})
        return cards

    def draw_shop(self, c):
        game = self.game
        w, h, gap = 200, 84, 8
        x0, y0 = (PANEL_W - (2 * w + gap)) / 2, 60
        for i, card in enumerate(self.shop_cards()):
            x = x0 + (i % 2) * (w + gap)
            y = y0 + (i // 2) * (h + gap)
            owned = card["owned"]
            affordable = game.coins >= card["cost"]
            icons.rrect(c, x, y, x + w, y + h, 12, fill="#dff0d8" if owned else CARD,
                        outline="#43a047" if owned else (data.GOLD if affordable else "#e6d4a0"), width=3)
            card["icon"](c, x + 42, y + 44, 1.15)
            label(c, x + 80, y + 20, card["name"], 10, INK, "w")
            if owned:
                icons.check(c, x + w - 24, y + 56, 1.1)
            else:
                icons.coin(c, x + 92, y + 58, 0.9)
                label(c, x + 106, y + 58, str(card["cost"]), 14, INK if affordable else BAD, "w")
            if card.get("badge") and not owned:
                c.create_oval(x + w - 30, y + 8, x + w - 10, y + 28, fill="#8e24aa", outline="white")
                label(c, x + w - 20, y + 18, str(card["badge"]), 9, "white")
            self.add_hit("panel", (x, y, x + w, y + h), None if owned else card["cb"], card["hint"], "buy:" + card["id"])

    def draw_journal(self, c):
        game = self.game
        icons.book(c, 30, 72, 0.9)
        icons.rrect(c, 56, 64, 330, 80, 7, fill="#efe2b8", outline="")
        icons.rrect(c, 56, 64, 56 + max(10, 274 * len(game.discovered) / len(data.CROPS)), 80, 7, fill="#43a047", outline="")
        label(c, 342, 72, str(len(game.discovered)) + "/" + str(len(data.CROPS)), 13, INK, "w")
        w, h = 94, 78
        for i, name in enumerate(data.CROPS):
            x = 17 + (i % 4) * (w + 6)
            y = 92 + (i // 4) * (h + 4)
            if name in game.discovered:
                icons.rrect(c, x, y, x + w, y + h, 10, fill=CARD, outline=data.GOLD, width=2)
                icons.crop_icon(c, x + w / 2, y + 30, name, 0.7)
                label(c, x + w / 2, y + h - 9, name, 9)
                self.add_hit("panel", (x, y, x + w, y + h), lambda n=name: self.select_seed(n),
                             name + ": " + data.CROPS[name]["blurb"], "stick:" + name)
            else:
                icons.rrect(c, x, y, x + w, y + h, 10, fill="#e6dfc8", outline="#d0c6a4", width=2)
                label(c, x + w / 2, y + h / 2, "?", 30, "#b9b29a")
                self.add_hit("panel", (x, y, x + w, y + h), None, "Undiscovered crop. Try a Mystery Seed Packet!")
        icons.trophy(c, 30, 273, 0.5)
        icons.rrect(c, 56, 266, 330, 282, 7, fill="#efe2b8", outline="")
        icons.rrect(c, 56, 266, 56 + max(10, 274 * len(game.achievements) / len(data.ACHIEVEMENTS)), 282, 7, fill=data.GOLD, outline="")
        label(c, 342, 274, str(len(game.achievements)) + "/" + str(len(data.ACHIEVEMENTS)), 13, INK, "w")
        for i, (name, desc) in enumerate(data.ACHIEVEMENTS.items()):
            x = 20 + (i % 3) * 138
            y = 296 + (i // 3) * 82
            unlocked = name in game.achievements
            icons.medal(c, x + 46, y + 28, 22, name, unlocked)
            label(c, x + 46, y + 66, name, 8, INK if unlocked else "#9e9e9e")
            self.add_hit("panel", (x, y, x + 92, y + 76), None, name + ": " + desc, "medal:" + name)

    # ==================================================================
    # Bottom dock: seeds and big buttons
    # ==================================================================
    def draw_dock(self):
        c = self.dock
        game = self.game
        c.delete("all")
        self.hits["dock"] = []
        icons.rrect(c, 0, 0, HUD_W, DOCK_H, 14, fill=BAR_BG, outline="")
        x = 10
        for i, name in enumerate(data.CROPS):
            info = data.CROPS[name]
            box = (x, 8, x + 60, DOCK_H - 8)
            if name in game.discovered:
                selected = name == self.crop and not self.boost_mode
                icons.rrect(c, *box, 10, fill=data.GOLD if selected else "#e9d9a8", outline="white" if selected else "", width=2)
                icons.crop_icon(c, x + 30, 38, name, 0.7)
                icons.coin(c, x + 15, 71, 0.4)
                label(c, x + 24, 71, str(info["seed"]), 8, INK, "w")
                icons.sun(c, x + 15, 88, 0.3)
                label(c, x + 24, 88, str(game.grow_days(name)), 8, INK, "w")
                label(c, x + 8, 15, str(i + 1), 7, "#8a7a55")
                self.add_hit("dock", box, lambda n=name: self.select_seed(n),
                             name + ": seed P" + str(info["seed"]) + ", grows in " + str(game.grow_days(name)) + " days, sells about P" + str(info["price"]) + ".",
                             "seed:" + name)
            else:
                icons.rrect(c, *box, 10, fill="#8a8672", outline="")
                icons.lock(c, x + 30, 46, 0.9, "#c9c3a8")
                self.add_hit("dock", box, None, "Undiscovered. Buy a Mystery Seed Packet in the Shop!", "seed:" + name)
            x += 63

        ready = game.ready_count()
        buttons = (("Water", icons.can, self.water_all, "Water all your crops (A).", "water_all", False),
                   ("Harvest", icons.basket, self.harvest_all, "Harvest everything that is ready (H).", "harvest_all", False),
                   ("Next", icons.target, self.next_up, "Which crop finishes first? (N)", "next", False),
                   ("Boost", icons.boost, self.toggle_boost, "Boost: click a crop to grow it 1 day (B).", "boost", self.boost_mode),
                   ("Sell", self.coin_stack, self.sell_all, "Sell all crates. (S sells the best one.)", "sell_all", False))
        for i, (text, draw, callback, hint, hid, active) in enumerate(buttons):
            bx = 524 + i * 66
            icons.rrect(c, bx, 8, bx + 62, DOCK_H - 8, 12, fill=data.GOLD if active else "#6aa56f", outline="white" if active else "", width=2)
            draw(c, bx + 31, 42, 1.0)
            label(c, bx + 31, 85, text, 9, INK if active else "white")
            if hid == "harvest_all" and ready:
                c.create_oval(bx + 40, 10, bx + 60, 30, fill=data.GOLD if (self.tick // 3) % 2 else "#ffe082", outline="#b8860b")
                label(c, bx + 50, 20, str(ready), 9)
            self.add_hit("dock", (bx, 8, bx + 62, DOCK_H - 8), callback, hint, hid)
        bx = 860
        grow = 2 * math.sin(self.tick * 0.25)
        icons.rrect(c, bx - grow, 8 - grow, bx + 116 + grow, DOCK_H - 8 + grow, 16, fill=data.GOLD, outline="#fff3c4", width=3)
        icons.moon(c, bx + 58, 42, 1.5, data.GOLD)
        label(c, bx + 58, 85, "END DAY", 12)
        self.add_hit("dock", (bx, 8, bx + 116, DOCK_H - 8), self.end_day, "Finish the day (Space): crops grow and a new day begins.", "end_day")

    @staticmethod
    def coin_stack(c, x, y, s=1.0):
        icons.coin(c, x - 6 * s, y + 8 * s, s * 0.9)
        icons.coin(c, x + 6 * s, y + 4 * s, s * 0.9)
        icons.coin(c, x, y - 6 * s, s * 0.9)

    # ==================================================================
    # Algo Lab (text for the teacher)
    # ==================================================================
    def refresh_lab(self):
        game = self.game
        text = self.lab_text
        text.config(state="normal")
        text.delete("1.0", "end")

        def section(title, lines, empty):
            text.insert("end", title + "\n", "head")
            if lines:
                for line in lines:
                    text.insert("end", "  " + line + "\n")
            else:
                text.insert("end", "  " + empty + "\n", "dim")
            text.insert("end", "\n")

        section("== BUBBLE SORT: market ranking ==", game.lab["bubble"], "(open the Market tab)")
        section("== INSERTION SORT: new crate -> Bodega ==", game.lab["insertion"], "(harvest a crop to see it)")
        section("== SELECTION SORT: Next Up / Sell Best ==", game.lab["selection"], "(press N after planting, or S to sell best)")
        count, lines = zones.tree_report(game.tree, game.is_ready)     # RECURSION
        section("== RECURSION: ready plots by zone (total " + str(count) + ") ==", lines, "")
        cell_text = str(self.hover) if self.hover is not None else "(move the mouse over a plot)"
        section("== TUPLE / SET / DICTIONARY ==", [
            "plot under mouse (tuple): " + cell_text,
            "discovered crops (set): {" + ", ".join(n for n in data.CROPS if n in game.discovered) + "}",
            "achievements (set): " + str(len(game.achievements)) + " unlocked",
            "crates by crop (dict): " + str(game.crop_counts()),
            "price index (dict): {" + ", ".join(n + ":" + ("%.2f" % game.index[n]) for n in data.CROPS if n in game.discovered) + "}",
        ], "")
        text.config(state="disabled")

    # ==================================================================
    # Full-screen overlays: start, help, end
    # ==================================================================
    def draw_overlay(self):
        c = self.overlay
        c.delete("all")
        self.hits["overlay"] = []
        if self.mode == "menu":
            self.draw_menu(c)
        elif self.mode == "help":
            self.draw_help(c)
        elif self.mode == "end":
            self.draw_end(c)

    def draw_backdrop(self, c, progress=0.15, weather=None):
        self.draw_sky(c, WIN_W, weather, progress, 880)
        c.create_rectangle(0, SCENE_H - 140, WIN_W, WIN_H, fill="#a5d86f", outline="")
        c.create_rectangle(0, WIN_H - 60, WIN_W, WIN_H, fill="#7a5230", outline="")
        for i, name in enumerate(data.CROPS):
            icons.draw_crop(c, 70 + i * 123, WIN_H - 14, name, 1.0, True, self.tick, 1.1)

    def draw_menu(self, c):
        self.draw_backdrop(c)
        label(c, 503, 83, "BUKID TYCOON", 54, "#3b2a1a")
        label(c, 500, 80, "BUKID TYCOON", 54, data.GOLD)
        icons.rrect(c, 380, 118, 620, 152, 17, fill="#c0392b", outline="#7b241c", width=3)
        label(c, 500, 135, "Fiesta Harvest", 17, "white")

        # the whole game in pictures
        icons.rrect(c, 90, 190, 910, 330, 20, fill=PANEL, outline=data.GOLD, width=4)
        steps = ((lambda x: icons.packet(c, x, 245, 1.2, False), "Plant"), (lambda x: icons.can(c, x, 245, 1.5), "Water"),
                 (lambda x: icons.basket(c, x, 245, 1.5), "Harvest"), (lambda x: self.coin_stack(c, x, 245, 1.3), "Sell"),
                 (lambda x: icons.moon(c, x, 245, 1.6, PANEL), "End day"))
        for i, (draw, text) in enumerate(steps):
            x = 170 + i * 165
            draw(x)
            label(c, x, 300, text, 13)
            if i < len(steps) - 1:
                c.create_polygon(x + 62, 233, x + 82, 245, x + 62, 257, fill=data.GOLD, outline="#b8860b")

        # goal
        goal = data.DIFFICULTIES[self.difficulty]
        icons.trophy(c, 370, 372, 1.0)
        icons.coin(c, 430, 372, 1.5)
        label(c, 452, 372, str(goal), 28, INK, "w")
        icons.sun(c, 610, 372, 1.5, self.tick)
        label(c, 636, 372, str(data.TOTAL_DAYS), 28, INK, "w")

        # difficulty
        for i, name in enumerate(data.DIFFICULTIES):
            x = 280 + i * 170
            selected = name == self.difficulty
            icons.rrect(c, x, 415, x + 150, 485, 14, fill=data.GOLD if selected else PANEL, outline="white" if selected else "#c9a23a", width=3)
            for k in range(i + 1):
                icons.star(c, x + 75 + (k - i / 2) * 26, 438, 11)
            label(c, x + 75, 470, name, 12)
            self.add_hit("overlay", (x, 415, x + 150, 485), lambda n=name: self.choose_difficulty(n), "Goal: " + str(data.DIFFICULTIES[name]) + " coins", "diff:" + name)

        # start
        bob = 3 * math.sin(self.tick * 0.2)
        icons.rrect(c, 330, 505 + bob, 670, 575 + bob, 24, fill="#43a047", outline="white", width=4)
        icons.play(c, 400, 540 + bob, 1.6)
        label(c, 530, 540 + bob, "START", 30, "white")
        self.add_hit("overlay", (330, 505, 670, 575), self.start_game, "Start the game", "start")
        for x, hid, callback, draw in ((60, "exit", self.root.destroy, lambda x: icons.cross(c, x, 540, 1.3)),
                                       (940, "help", self.show_help, lambda x: icons.help_icon(c, x, 540, 1.3))):
            c.create_oval(x - 28, 512, x + 28, 568, fill="#2f5d34", outline="white", width=3)
            draw(x)
            self.add_hit("overlay", (x - 28, 512, x + 28, 568), callback, "", hid)

    def choose_difficulty(self, name):
        self.difficulty = name
        self.sound.play("click")

    def draw_help(self, c):
        self.draw_backdrop(c)
        icons.rrect(c, 60, 40, 940, 610, 24, fill=PANEL, outline=data.GOLD, width=5)
        icons.help_icon(c, 100, 80, 1.5)
        label(c, 140, 80, "How to play", 28, INK, "w")
        rows = (("Click", lambda x, y: (icons.crop_icon(c, x - 26, y, "Mais", 0.35), icons.can(c, x, y, 0.5), icons.basket(c, x + 28, y, 0.5)), "plant, water, harvest"),
                ("Drag", lambda x, y: icons.field_icon(c, x, y, 0.8), "paint many plots"),
                ("A", lambda x, y: icons.can(c, x, y, 0.8), "water all"),
                ("H", lambda x, y: icons.basket(c, x, y, 0.8), "harvest all"),
                ("S", lambda x, y: icons.coin(c, x, y, 1.0), "sell best crate"),
                ("N", lambda x, y: icons.target(c, x, y, 0.8), "next crop to finish"),
                ("B", lambda x, y: icons.boost(c, x, y, 0.8), "boost a crop"),
                ("Space", lambda x, y: icons.moon(c, x, y, 0.9, PANEL), "end the day"),
                ("1-8", lambda x, y: icons.packet(c, x, y, 0.7, False), "pick a seed"),
                ("M", lambda x, y: icons.speaker(c, x, y, 0.9, True) if False else (c.create_oval(x - 14, y - 14, x + 14, y + 14, fill="#4b7f52", outline=""), icons.speaker(c, x, y, 0.8, True)), "sound on / off"),
                ("?", lambda x, y: icons.help_icon(c, x, y, 0.8), "this help"),
                ("Esc", lambda x, y: (c.create_oval(x - 14, y - 14, x + 14, y + 14, fill="#4b7f52", outline=""), icons.home(c, x, y, 0.8)), "main menu"))
        for i, (key, draw, text) in enumerate(rows):
            col, row = i % 2, i // 2
            x = 90 + col * 430
            y = 140 + row * 70
            icons.rrect(c, x, y, x + 78, y + 44, 8, fill="#fff9ea", outline="#8a5f2c", width=3)
            label(c, x + 39, y + 22, key, 14)
            draw(x + 135, y + 22)
            label(c, x + 195, y + 22, text, 13, INK, "w")
        label(c, 500, 590, "click anywhere to close", 11, "#8a7a55")
        self.add_hit("overlay", (0, 0, WIN_W, WIN_H), self.close_help, "", "close")

    def draw_end(self, c):
        game = self.game
        won = game.won
        self.draw_backdrop(c, 0.1 if won else 0.95, None if won else "rain")
        icons.rrect(c, 180, 40, 820, 610, 28, fill=PANEL, outline=data.GOLD, width=5)
        bounce = 6 * math.sin(self.tick * 0.3)
        if won:
            icons.trophy(c, 500, 140 + bounce, 3.0)
            label(c, 500, 245, "MABUHAY!", 40, GOOD)
        else:
            icons.scarecrow(c, 500, 160, 2.6)
            label(c, 500, 245, "Season over", 36, BAD)
        stars = sum(1 for minimum, _ in data.RANKS[1:] if game.coins >= minimum * game.goal)
        for i in range(3):
            icons.star(c, 430 + i * 70, 305, 28, "#ffca28" if i < stars else "#e0d8c0", "#b8860b" if i < stars else "#c9c0a0")
        label(c, 500, 355, game.rank(), 14)
        stats = ((icons.coin, str(game.coins)), (icons.basket, str(game.stats["harvested"])),
                 (icons.book, str(len(game.discovered)) + "/" + str(len(data.CROPS))),
                 (icons.trophy, str(len(game.achievements)) + "/" + str(len(data.ACHIEVEMENTS))))
        for i, (draw, text) in enumerate(stats):
            x = 270 + i * 140
            icons.rrect(c, x - 55, 385, x + 55, 455, 14, fill=CARD, outline="#e6d4a0", width=2)
            draw(c, x - 22, 420, 0.9 if draw is not icons.trophy else 0.5)
            label(c, x + 6, 420, text, 14, INK, "w")
        for x, hid, callback, draw, color in ((330, "again", self.start_game, lambda x: icons.restart(c, x, 540, 1.5), "#43a047"),
                                              (500, "menu", self.show_menu, lambda x: icons.home(c, x, 540, 1.5), "#6aa56f"),
                                              (670, "exit", self.root.destroy, lambda x: icons.cross(c, x, 540, 1.5), "#8a8672")):
            icons.rrect(c, x - 60, 500, x + 60, 580, 20, fill=color, outline="white", width=4)
            draw(x)
            self.add_hit("overlay", (x - 60, 500, x + 60, 580), callback, "", hid)
        alive = []
        for piece in self.confetti:
            c.create_rectangle(piece["x"], piece["y"], piece["x"] + 7, piece["y"] + 7, fill=piece["color"], outline="")
            piece["y"] += piece["vy"]
            piece["x"] += math.sin(piece["y"] * 0.05) * 1.5
            if piece["y"] < WIN_H:
                alive.append(piece)
            else:
                piece["y"] = -10
                alive.append(piece)
        self.confetti = alive
