"""Static game data and settings for Bukid Tycoon.

Everything the designers might want to tweak (prices, goal, events, ...) lives here.
"""

GAME_TITLE = "BUKID TYCOON: Fiesta Harvest"

# ---- Rules / balance -------------------------------------------------------
TOTAL_DAYS = 30
START_COINS = 150
# difficulty name -> coin goal (a dictionary the start screen reads)
DIFFICULTIES = {"Easy": 1500, "Normal": 3000, "Hard": 4500}
GOAL_COINS = DIFFICULTIES["Normal"]
BASE_CAPACITY = 12            # crates the Bodega (storage) can hold at the start
BODEGA_BONUS = 12             # extra crates after the Bodega upgrade
EVENT_CHANCE = 0.45           # chance of a random event each new day
FIESTA_DAYS = (10, 20, 30)    # tuple: fixed days of the Barangay Fiesta
MYSTERY_PACKET_COST = 40
RUSH_COST = 25
WATER_COST = 2                # coins to water one plot
SALE_DROP = 0.03              # each crate sold lowers that crop's price index by 3%
MIN_INDEX = 0.45
MAX_INDEX = 2.2

# ---- Farm layout -----------------------------------------------------------
GRID_ROWS = 4
GRID_COLS = 6

# Each field covers 2 columns; every field has 2 beds (upper and lower).
# cols and rows are TUPLES (first, last) because they never change.
FIELDS = (
    {"name": "Bahay Kubo Field", "short": "Kubo", "cols": (0, 1), "cost": 0},
    {"name": "Ilog Field", "short": "Ilog", "cols": (2, 3), "cost": 250},
    {"name": "Burol Field", "short": "Burol", "cols": (4, 5), "cost": 500},
)
BEDS = (("Upper bed", (0, 1)), ("Lower bed", (2, 3)))

# ---- Crops (dictionary of dictionaries) ------------------------------------
# seed  = cost to plant      grow = days until ready      price = base sell price
CROPS = {
    "Kangkong": {"seed": 5,  "grow": 2, "price": 12,  "color": "#43a047", "shape": "stalk", "start": True,
                 "blurb": "Water spinach. Super fast, tiny profit."},
    "Mais":     {"seed": 10, "grow": 3, "price": 28,  "color": "#fdd835", "shape": "ear", "start": True,
                 "blurb": "Corn. A reliable early earner."},
    "Kamatis":  {"seed": 14, "grow": 3, "price": 36,  "color": "#e53935", "shape": "round", "start": True,
                 "blurb": "Tomato. Quick and juicy."},
    "Talong":   {"seed": 18, "grow": 4, "price": 54,  "color": "#8e24aa", "shape": "oval", "start": False,
                 "blurb": "Eggplant. Good money for a short wait."},
    "Palay":    {"seed": 25, "grow": 5, "price": 85,  "color": "#e0b232", "shape": "grain", "start": False,
                 "blurb": "Rice. The heart of every barangay."},
    "Saging":   {"seed": 40, "grow": 6, "price": 150, "color": "#ffeb3b", "shape": "bunch", "start": False,
                 "blurb": "Banana. Slow but rewarding."},
    "Ube":      {"seed": 55, "grow": 6, "price": 200, "color": "#7e57c2", "shape": "oval", "start": False,
                 "blurb": "Purple yam. A fiesta favourite."},
    "Mangga":   {"seed": 70, "grow": 7, "price": 270, "color": "#fb8c00", "shape": "oval", "start": False,
                 "blurb": "Mango. The most valuable crop of all."},
}

# ---- Quality (dictionary) --------------------------------------------------
QUALITY = {"Normal": 1.0, "Fine": 1.25, "Premium": 1.6}
# Chance weights depend on how many days the crop was watered while growing.
QUALITY_ODDS = {
    "high": {"Premium": 45, "Fine": 40, "Normal": 15},   # watered >= 80% of days
    "mid":  {"Premium": 15, "Fine": 45, "Normal": 40},   # watered >= 50% of days
    "low":  {"Premium": 3,  "Fine": 22, "Normal": 75},
}
QUALITY_COLORS = {"Normal": "#ffffff", "Fine": "#d7f0ff", "Premium": "#ffe9a8"}

# ---- Upgrades --------------------------------------------------------------
UPGRADES = {
    "Irrigation":   {"cost": 220, "desc": "Canals bring water: every crop grows 1 day faster (min. 2 days)."},
    "Bodega":       {"cost": 120, "desc": "A bigger storage hut: +12 crate slots."},
    "Storm Shield": {"cost": 160, "desc": "Bamboo windbreaks: typhoons can no longer destroy plants."},
    "Scarecrow":    {"cost": 70,  "desc": "Kuya Berto's scarecrow chases pests away."},
}

# ---- Random events (weights decide how often each one happens) -------------
EVENTS = {
    "rain":     {"weight": 3},
    "typhoon":  {"weight": 1},
    "pests":    {"weight": 2},
    "glut":     {"weight": 2},
    "demand":   {"weight": 2},
    "gift":     {"weight": 1},
    "seedswap": {"weight": 1},
}

# ---- Achievements (a SET of unlocked names is kept by the game) ------------
ACHIEVEMENTS = {
    "First Harvest": "Harvest your very first crop.",
    "Premium Pick":  "Harvest a Premium quality crop.",
    "Big Sale":      "Earn P500 or more from one selling spree.",
    "Land Baron":    "Own all three fields.",
    "Naturalist":    "Discover all 8 crops.",
    "Storm Survivor": "Come through a typhoon without losing a plant.",
}

# ---- Ranks shown on the final screen ---------------------------------------
# (multiple of the goal, title): e.g. 1.0 means "reached the goal"
RANKS = (
    (0.0, "Batang Magsasaka (Farm Rookie)"),
    (0.6, "Masipag na Magsasaka (Hard Worker)"),
    (1.0, "Kapitan ng Bukid (Farm Captain)"),
    (1.8, "Alamat ng Bukid (Farm Legend)"),
)

# ---- Colours for the interface --------------------------------------------
BG = "#fff6e0"
DARK = "#2f5d34"
GOLD = "#f2b632"
SOIL = "#8b5a35"
SOIL_WET = "#5f3b21"
