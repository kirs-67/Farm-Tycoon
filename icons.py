"""Every picture in Bukid Tycoon, drawn with Tkinter canvas shapes (no image files).

All functions look like  name(canvas, x, y, s=1.0, ...)
    x, y  the CENTRE of the picture
    s     size multiplier (1.0 is about 40 pixels wide)
"""

import math

import data

GOLD = "#f2b632"
INK = "#3b2a1a"
GREEN = "#2e7d32"
LEAF = "#56b04f"
WATER = "#4aa3e8"


# ----------------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------------
def rrect(c, x1, y1, x2, y2, r=10, **options):
    """Rounded rectangle."""
    r = min(r, (x2 - x1) / 2, (y2 - y1) / 2)
    points = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2, x2 - r, y2,
              x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return c.create_polygon(points, smooth=True, **options)


def star(c, x, y, r, fill="#ffca28", outline="#b8860b"):
    points = []
    for k in range(10):
        radius = r if k % 2 == 0 else r * 0.45
        angle = -math.pi / 2 + k * math.pi / 5
        points += [x + math.cos(angle) * radius, y + math.sin(angle) * radius]
    c.create_polygon(points, fill=fill, outline=outline)


def font(size, bold=True):
    return ("Helvetica", max(6, int(size)), "bold" if bold else "normal")


# ----------------------------------------------------------------------------
# Money, time, weather
# ----------------------------------------------------------------------------
def coin(c, x, y, s=1.0):
    r = 10 * s
    c.create_oval(x - r, y - r, x + r, y + r, fill="#ffca28", outline="#b8860b", width=max(1, 2 * s))
    c.create_oval(x - r * 0.62, y - r * 0.62, x + r * 0.62, y + r * 0.62, outline="#e6a800")
    c.create_text(x, y, text="P", fill="#8a5a00", font=font(9 * s))


def sun(c, x, y, s=1.0, tick=0):
    for k in range(8):
        angle = tick * 0.05 + k * math.pi / 4
        c.create_line(x + math.cos(angle) * 11 * s, y + math.sin(angle) * 11 * s,
                      x + math.cos(angle) * 16 * s, y + math.sin(angle) * 16 * s, fill="#ffd54f", width=max(1, 2 * s))
    c.create_oval(x - 9 * s, y - 9 * s, x + 9 * s, y + 9 * s, fill="#ffca28", outline="#ffb300", width=max(1, 2 * s))


def moon(c, x, y, s=1.0, bg="#2f5d34"):
    c.create_oval(x - 11 * s, y - 11 * s, x + 11 * s, y + 11 * s, fill="#ffe082", outline="")
    c.create_oval(x - 4 * s, y - 14 * s, x + 16 * s, y + 8 * s, fill=bg, outline="")
    star(c, x + 11 * s, y - 9 * s, 3.5 * s)
    star(c, x + 15 * s, y + 3 * s, 2.5 * s)


def cloud(c, x, y, s=1.0, color="#ffffff"):
    for dx, dy, w in ((-10, 3, 14), (0, -3, 18), (11, 3, 14), (1, 6, 24)):
        c.create_oval(x + (dx - w / 2) * s, y + (dy - 7) * s, x + (dx + w / 2) * s, y + (dy + 7) * s, fill=color, outline="")


def drop(c, x, y, s=1.0, filled=True, color=WATER):
    kw = {"fill": color, "outline": ""} if filled else {"fill": "", "outline": color, "width": max(1, 2 * s)}
    c.create_polygon(x, y - 9 * s, x - 5.5 * s, y - 1 * s, x + 5.5 * s, y - 1 * s, **kw)
    c.create_oval(x - 5.5 * s, y - 3 * s, x + 5.5 * s, y + 8 * s, **kw)


def arrow(c, x, y, s=1.0, up=True, color=GREEN):
    d = -1 if up else 1
    c.create_polygon(x, y + d * 7 * s, x - 7 * s, y - d * 5 * s, x + 7 * s, y - d * 5 * s, fill=color, outline="")


def flag(c, x, y, s=1.0, color="#e53935"):
    c.create_line(x - 6 * s, y + 12 * s, x - 6 * s, y - 12 * s, fill="#5d3d1f", width=max(1, 2 * s))
    c.create_polygon(x - 6 * s, y - 12 * s, x + 10 * s, y - 6 * s, x - 6 * s, y, fill=color, outline="")


def bug(c, x, y, s=1.0):
    for dy in (-4, 0, 4):
        c.create_line(x - 9 * s, y + dy * s, x + 9 * s, y + dy * s, fill="#212121", width=max(1, s))
    c.create_oval(x - 6 * s, y - 8 * s, x + 6 * s, y + 8 * s, fill="#5d4037", outline="#212121")
    c.create_oval(x - 4 * s, y - 12 * s, x + 4 * s, y - 6 * s, fill="#212121", outline="")


def gift(c, x, y, s=1.0):
    c.create_rectangle(x - 10 * s, y - 4 * s, x + 10 * s, y + 10 * s, fill="#e53935", outline="#8e0000")
    c.create_rectangle(x - 12 * s, y - 9 * s, x + 12 * s, y - 3 * s, fill="#ef5350", outline="#8e0000")
    c.create_rectangle(x - 2 * s, y - 9 * s, x + 2 * s, y + 10 * s, fill="#ffd54f", outline="")
    c.create_oval(x - 7 * s, y - 15 * s, x, y - 8 * s, outline="#ffd54f", width=max(1, 2 * s))
    c.create_oval(x, y - 15 * s, x + 7 * s, y - 8 * s, outline="#ffd54f", width=max(1, 2 * s))


def swirl(c, x, y, s=1.0, tick=0):
    for k, r in enumerate((14, 10, 6)):
        c.create_arc(x - r * s, y - r * s, x + r * s, y + r * s, start=tick * 12 + k * 100, extent=250,
                     style="arc", outline="#cfd8dc", width=max(1, 3 * s))


def event_icon(c, x, y, s, name, tick=0):
    """A small picture for today's event (or a sun when nothing special happens)."""
    if name == "rain":
        cloud(c, x, y - 4 * s, s * 0.9, "#90a4ae")
        for dx in (-8, 0, 8):
            drop(c, x + dx * s, y + 11 * s, s * 0.45)
    elif name == "typhoon":
        cloud(c, x, y - 8 * s, s * 0.9, "#546e7a")
        swirl(c, x, y + 6 * s, s * 0.8, tick)
    elif name == "pests":
        bug(c, x, y, s)
    elif name == "glut":
        arrow(c, x - 7 * s, y, s, up=False, color="#c62828")
        coin(c, x + 8 * s, y, s * 0.8)
    elif name == "demand":
        arrow(c, x - 7 * s, y, s, up=True, color=GREEN)
        coin(c, x + 8 * s, y, s * 0.8)
    elif name == "gift":
        gift(c, x, y, s * 0.9)
    elif name == "seedswap":
        packet(c, x, y, s * 0.8)
    elif name == "fiesta":
        flag(c, x - 6 * s, y, s * 0.9, "#e53935")
        flag(c, x + 8 * s, y, s * 0.9, "#1e88e5")
    else:
        sun(c, x, y, s * 0.85, tick)


# ----------------------------------------------------------------------------
# Tools and buttons
# ----------------------------------------------------------------------------
def can(c, x, y, s=1.0):
    c.create_line(x + 8 * s, y, x + 18 * s, y - 9 * s, fill="#2b6cb0", width=max(2, 4 * s))
    c.create_arc(x - 20 * s, y - 8 * s, x - 6 * s, y + 8 * s, start=90, extent=180, style="arc",
                 outline="#2b6cb0", width=max(1, 3 * s))
    rrect(c, x - 12 * s, y - 6 * s, x + 10 * s, y + 12 * s, 4 * s, fill="#5aa9e6", outline="#2b6cb0", width=max(1, 2 * s))
    for dx, dy in ((20, -3), (23, 3), (17, 4)):
        drop(c, x + dx * s, y + dy * s, s * 0.35)


def basket(c, x, y, s=1.0, produce=True):
    c.create_arc(x - 12 * s, y - 20 * s, x + 12 * s, y + 4 * s, start=0, extent=180, style="arc",
                 outline="#7a4a1d", width=max(1, 3 * s))
    if produce:
        for dx, color in ((-6, "#e53935"), (0, "#fdd835"), (6, "#7cb342")):
            c.create_oval(x + (dx - 5) * s, y - 8 * s, x + (dx + 5) * s, y + 2 * s, fill=color, outline="")
    c.create_polygon(x - 15 * s, y - 2 * s, x + 15 * s, y - 2 * s, x + 11 * s, y + 13 * s, x - 11 * s, y + 13 * s,
                     fill="#c68642", outline="#7a4a1d", width=max(1, 2 * s))
    for k in (-6, 0, 6):
        c.create_line(x + k * s, y - 1 * s, x + k * 0.8 * s, y + 12 * s, fill="#8d5a28")
    c.create_line(x - 13 * s, y + 5 * s, x + 13 * s, y + 5 * s, fill="#8d5a28")


def target(c, x, y, s=1.0):
    for r, color in ((14, "#e53935"), (10, "#ffffff"), (6, "#e53935"), (2.5, "#ffffff")):
        c.create_oval(x - r * s, y - r * s, x + r * s, y + r * s, fill=color, outline="#7f1d1d")
    c.create_line(x - 17 * s, y, x + 17 * s, y, fill="#7f1d1d", width=max(1, s))
    c.create_line(x, y - 17 * s, x, y + 17 * s, fill="#7f1d1d", width=max(1, s))


def boost(c, x, y, s=1.0):
    c.create_oval(x - 13 * s, y - 6 * s, x + 13 * s, y + 14 * s, fill="#a1887f", outline="#5d4037", width=max(1, 2 * s))
    c.create_polygon(x - 6 * s, y - 4 * s, x - 3 * s, y - 13 * s, x + 3 * s, y - 13 * s, x + 6 * s, y - 4 * s,
                     fill="#bcaaa4", outline="#5d4037")
    c.create_line(x - 5 * s, y + 4 * s, x + 5 * s, y + 4 * s, fill="white", width=max(2, 3 * s))
    c.create_line(x, y - 1 * s, x, y + 9 * s, fill="white", width=max(2, 3 * s))
    star(c, x + 14 * s, y - 10 * s, 5 * s)
    star(c, x - 15 * s, y - 6 * s, 3.5 * s)


def speaker(c, x, y, s=1.0, on=True):
    c.create_polygon(x - 12 * s, y - 4 * s, x - 6 * s, y - 4 * s, x + 1 * s, y - 11 * s, x + 1 * s, y + 11 * s,
                     x - 6 * s, y + 4 * s, x - 12 * s, y + 4 * s, fill="#ffffff", outline="")
    if on:
        for r in (6, 10):
            c.create_arc(x + 1 * s - r * s, y - r * s, x + 1 * s + r * s, y + r * s, start=-45, extent=90,
                         style="arc", outline="#ffffff", width=max(1, 2 * s))
    else:
        c.create_line(x + 5 * s, y - 6 * s, x + 15 * s, y + 6 * s, fill="#ff8a80", width=max(2, 3 * s))
        c.create_line(x + 5 * s, y + 6 * s, x + 15 * s, y - 6 * s, fill="#ff8a80", width=max(2, 3 * s))


def help_icon(c, x, y, s=1.0):
    c.create_oval(x - 12 * s, y - 12 * s, x + 12 * s, y + 12 * s, fill="#fff3d6", outline="#ffffff", width=max(1, 2 * s))
    c.create_text(x, y, text="?", fill=INK, font=font(15 * s))


def home(c, x, y, s=1.0):
    c.create_polygon(x - 13 * s, y - 1 * s, x, y - 13 * s, x + 13 * s, y - 1 * s, fill="#ffffff", outline="")
    c.create_rectangle(x - 9 * s, y - 1 * s, x + 9 * s, y + 11 * s, fill="#ffffff", outline="")
    c.create_rectangle(x - 3 * s, y + 3 * s, x + 3 * s, y + 11 * s, fill="#6d4c2a", outline="")


def restart(c, x, y, s=1.0):
    c.create_arc(x - 10 * s, y - 10 * s, x + 10 * s, y + 10 * s, start=40, extent=280, style="arc",
                 outline="#ffffff", width=max(2, 3 * s))
    c.create_polygon(x + 9 * s, y - 12 * s, x + 14 * s, y - 2 * s, x + 3 * s, y - 3 * s, fill="#ffffff", outline="")


def play(c, x, y, s=1.0, color="#ffffff"):
    c.create_polygon(x - 8 * s, y - 11 * s, x + 12 * s, y, x - 8 * s, y + 11 * s, fill=color, outline="")


def cross(c, x, y, s=1.0, color="#ffffff"):
    c.create_line(x - 8 * s, y - 8 * s, x + 8 * s, y + 8 * s, fill=color, width=max(2, 3 * s))
    c.create_line(x - 8 * s, y + 8 * s, x + 8 * s, y - 8 * s, fill=color, width=max(2, 3 * s))


def check(c, x, y, s=1.0):
    c.create_oval(x - 10 * s, y - 10 * s, x + 10 * s, y + 10 * s, fill="#43a047", outline="#1b5e20", width=max(1, 2 * s))
    c.create_line(x - 5 * s, y, x - 1 * s, y + 5 * s, x + 6 * s, y - 5 * s, fill="white", width=max(2, 3 * s))


def lock(c, x, y, s=1.0, color="#ffe082"):
    c.create_arc(x - 8 * s, y - 16 * s, x + 8 * s, y + 2 * s, start=0, extent=180, style="arc", outline=color,
                 width=max(2, 3 * s))
    rrect(c, x - 11 * s, y - 4 * s, x + 11 * s, y + 13 * s, 3 * s, fill=color, outline="#8a5a00", width=max(1, 2 * s))
    c.create_oval(x - 2 * s, y + 2 * s, x + 2 * s, y + 6 * s, fill="#8a5a00", outline="")


# ----------------------------------------------------------------------------
# Tab pictures and shop pictures
# ----------------------------------------------------------------------------
def chart(c, x, y, s=1.0):
    for dx, h, color in ((-10, 12, "#e53935"), (0, 22, "#43a047"), (10, 17, "#fbc02d")):
        c.create_rectangle(x + (dx - 4) * s, y + (12 - h) * s, x + (dx + 4) * s, y + 12 * s, fill=color, outline=INK)
    c.create_line(x - 15 * s, y + 12 * s, x + 15 * s, y + 12 * s, fill=INK, width=max(1, 2 * s))


def crate(c, x, y, s=1.0, fill="#d9a05b"):
    c.create_rectangle(x - 14 * s, y - 10 * s, x + 14 * s, y + 11 * s, fill=fill, outline="#6d4524", width=max(1, 2 * s))
    for dy in (-3, 4):
        c.create_line(x - 14 * s, y + dy * s, x + 14 * s, y + dy * s, fill="#8a5f2c", width=max(1, 2 * s))
    c.create_line(x - 14 * s, y - 10 * s, x + 14 * s, y + 11 * s, fill="#8a5f2c", width=max(1, s))
    c.create_line(x + 14 * s, y - 10 * s, x - 14 * s, y + 11 * s, fill="#8a5f2c", width=max(1, s))


def stall(c, x, y, s=1.0):
    for k in range(6):
        c.create_rectangle(x + (-15 + k * 5) * s, y - 12 * s, x + (-10 + k * 5) * s, y - 3 * s,
                           fill="#e53935" if k % 2 == 0 else "#ffffff", outline="#8e0000")
    c.create_rectangle(x - 13 * s, y - 3 * s, x + 13 * s, y + 12 * s, fill="#c68642", outline="#6d4524")
    coin(c, x, y + 4 * s, 0.6 * s)


def book(c, x, y, s=1.0):
    c.create_polygon(x - 15 * s, y - 9 * s, x, y - 5 * s, x, y + 11 * s, x - 15 * s, y + 7 * s, fill="#fff8e1", outline="#6d4524")
    c.create_polygon(x + 15 * s, y - 9 * s, x, y - 5 * s, x, y + 11 * s, x + 15 * s, y + 7 * s, fill="#ffecb3", outline="#6d4524")
    star(c, x - 7 * s, y, 3.5 * s)
    c.create_oval(x + 3 * s, y - 3 * s, x + 11 * s, y + 3 * s, fill=LEAF, outline="")


def flask(c, x, y, s=1.0):
    c.create_polygon(x - 5 * s, y - 13 * s, x + 5 * s, y - 13 * s, x + 5 * s, y - 4 * s, x + 14 * s, y + 11 * s,
                     x - 14 * s, y + 11 * s, x - 5 * s, y - 4 * s, fill="#e0f7fa", outline="#37474f", width=max(1, 2 * s))
    c.create_polygon(x - 9 * s, y + 3 * s, x + 9 * s, y + 3 * s, x + 14 * s, y + 11 * s, x - 14 * s, y + 11 * s,
                     fill="#66bb6a", outline="")
    for dx, dy, r in ((-3, 0, 2), (3, -4, 1.5), (0, -8, 1.5)):
        c.create_oval(x + (dx - r) * s, y + (dy - r) * s, x + (dx + r) * s, y + (dy + r) * s, fill="white", outline="#37474f")


def trophy(c, x, y, s=1.0):
    c.create_arc(x - 20 * s, y - 12 * s, x - 6 * s, y + 4 * s, start=90, extent=180, style="arc", outline="#b8860b", width=max(2, 3 * s))
    c.create_arc(x + 6 * s, y - 12 * s, x + 20 * s, y + 4 * s, start=-90, extent=180, style="arc", outline="#b8860b", width=max(2, 3 * s))
    c.create_polygon(x - 12 * s, y - 14 * s, x + 12 * s, y - 14 * s, x + 9 * s, y + 4 * s, x + 3 * s, y + 9 * s,
                     x - 3 * s, y + 9 * s, x - 9 * s, y + 4 * s, fill="#ffca28", outline="#b8860b", width=max(1, 2 * s))
    c.create_rectangle(x - 3 * s, y + 8 * s, x + 3 * s, y + 14 * s, fill="#ffca28", outline="#b8860b")
    c.create_rectangle(x - 9 * s, y + 13 * s, x + 9 * s, y + 18 * s, fill="#8d6e63", outline="#4e342e")
    star(c, x, y - 4 * s, 5 * s, "#fff8e1")


def packet(c, x, y, s=1.0, question=True):
    c.create_polygon(x - 11 * s, y - 14 * s, x + 11 * s, y - 14 * s, x + 12 * s, y + 14 * s, x - 12 * s, y + 14 * s,
                     fill="#fff3c4", outline="#8a5f2c", width=max(1, 2 * s))
    c.create_polygon(x - 11 * s, y - 14 * s, x + 11 * s, y - 14 * s, x + 9 * s, y - 8 * s, x - 9 * s, y - 8 * s,
                     fill="#e57373", outline="#8a5f2c")
    if question:
        c.create_text(x, y + 3 * s, text="?", fill="#8e24aa", font=font(18 * s))


def field_icon(c, x, y, s=1.0):
    c.create_rectangle(x - 17 * s, y - 11 * s, x + 17 * s, y + 11 * s, fill="#8b5a35", outline="#4a3018", width=max(1, 2 * s))
    for dy in (-5, 0, 5):
        c.create_line(x - 14 * s, y + dy * s, x + 14 * s, y + dy * s, fill="#6d4524", width=max(1, s))
    for dx in (-9, 0, 9):
        c.create_oval(x + (dx - 3) * s, y - 3 * s, x + (dx + 3) * s, y + 3 * s, fill=LEAF, outline="")


def barn(c, x, y, s=1.0):
    c.create_rectangle(x - 14 * s, y - 4 * s, x + 14 * s, y + 13 * s, fill="#c0392b", outline="#7b241c", width=max(1, 2 * s))
    c.create_polygon(x - 17 * s, y - 3 * s, x, y - 15 * s, x + 17 * s, y - 3 * s, fill="#e57373", outline="#7b241c")
    c.create_rectangle(x - 5 * s, y + 3 * s, x + 5 * s, y + 13 * s, fill="#f5f5f5", outline="#7b241c")
    c.create_line(x - 5 * s, y + 3 * s, x + 5 * s, y + 13 * s, fill="#7b241c")
    c.create_line(x + 5 * s, y + 3 * s, x - 5 * s, y + 13 * s, fill="#7b241c")


def canal(c, x, y, s=1.0):
    c.create_rectangle(x - 17 * s, y - 6 * s, x + 17 * s, y + 8 * s, fill="#4fc3f7", outline="#0277bd", width=max(1, 2 * s))
    for dx in (-10, 0, 10):
        c.create_line(x + dx * s, y - 1 * s, x + (dx + 4) * s, y + 3 * s, fill="#e1f5fe", width=max(1, 2 * s))
    drop(c, x, y - 14 * s, s * 0.6)


def shield(c, x, y, s=1.0):
    c.create_polygon(x - 13 * s, y - 12 * s, x + 13 * s, y - 12 * s, x + 13 * s, y + 2 * s, x, y + 15 * s, x - 13 * s, y + 2 * s,
                     fill="#42a5f5", outline="#0d47a1", width=max(1, 2 * s))
    cloud(c, x, y - 2 * s, s * 0.7, "#ffffff")
    c.create_line(x - 4 * s, y + 6 * s, x - 6 * s, y + 10 * s, fill="#0d47a1", width=max(1, 2 * s))


def scarecrow(c, x, y, s=1.0):
    c.create_line(x, y - 14 * s, x, y + 14 * s, fill="#6d4c2a", width=max(2, 3 * s))
    c.create_line(x - 14 * s, y - 4 * s, x + 14 * s, y - 4 * s, fill="#6d4c2a", width=max(2, 3 * s))
    c.create_oval(x - 6 * s, y - 24 * s, x + 6 * s, y - 12 * s, fill="#f4d58d", outline="#8a5f2c")
    c.create_polygon(x - 9 * s, y - 21 * s, x, y - 33 * s, x + 9 * s, y - 21 * s, fill="#8e24aa", outline="")
    c.create_rectangle(x - 7 * s, y - 12 * s, x + 7 * s, y + 4 * s, fill="#e53935", outline="")


def upgrade_icon(c, x, y, s, name):
    {"Irrigation": canal, "Bodega": barn, "Storm Shield": shield, "Scarecrow": scarecrow}[name](c, x, y, s)


def medal(c, x, y, r, kind, unlocked=True):
    """A round medal. Locked medals are grey."""
    base = "#ffca28" if unlocked else "#bdbdbd"
    edge = "#b8860b" if unlocked else "#8d8d8d"
    ink = "#7a4a00" if unlocked else "#9e9e9e"
    c.create_polygon(x - r * 0.7, y + r * 0.4, x - r * 0.2, y + r * 1.5, x - r * 0.9, y + r * 1.3, fill="#e53935" if unlocked else "#bdbdbd", outline="")
    c.create_polygon(x + r * 0.7, y + r * 0.4, x + r * 0.2, y + r * 1.5, x + r * 0.9, y + r * 1.3, fill="#1e88e5" if unlocked else "#bdbdbd", outline="")
    c.create_oval(x - r, y - r, x + r, y + r, fill=base, outline=edge, width=2)
    k = r / 20.0
    if kind == "First Harvest":
        c.create_line(x, y + 9 * k, x, y - 3 * k, fill=ink, width=max(2, 3 * k))
        c.create_oval(x - 9 * k, y - 8 * k, x, y - 1 * k, fill=ink, outline="")
        c.create_oval(x, y - 10 * k, x + 9 * k, y - 3 * k, fill=ink, outline="")
    elif kind == "Premium Pick":
        star(c, x, y, 11 * k, "#fff8e1" if unlocked else "#eeeeee", ink)
    elif kind == "Big Sale":
        c.create_text(x, y, text="P", fill=ink, font=font(22 * k))
    elif kind == "Land Baron":
        flag(c, x, y, k * 0.9, ink)
    elif kind == "Naturalist":
        c.create_oval(x - 10 * k, y - 6 * k, x + 10 * k, y + 6 * k, fill=ink, outline="")
        c.create_line(x - 10 * k, y + 6 * k, x + 10 * k, y - 6 * k, fill=base, width=max(1, 2 * k))
    else:                                           # Storm Survivor
        cloud(c, x, y - 2 * k, k * 0.9, ink)
        c.create_line(x - 2 * k, y + 5 * k, x - 5 * k, y + 11 * k, fill=ink, width=max(2, 3 * k))


def farmer(c, x, y, s=1.0):
    """Kuya Berto's face, who gives the hints."""
    c.create_oval(x - 9 * s, y - 8 * s, x + 9 * s, y + 10 * s, fill="#f2c28b", outline="#8a5f2c")
    c.create_oval(x - 15 * s, y - 6 * s, x + 15 * s, y + 1 * s, fill="#e2c15a", outline="#a8812c")
    c.create_polygon(x - 8 * s, y - 5 * s, x - 5 * s, y - 15 * s, x + 5 * s, y - 15 * s, x + 8 * s, y - 5 * s, fill="#e2c15a", outline="#a8812c")
    c.create_oval(x - 4 * s, y + 1 * s, x - 2 * s, y + 3 * s, fill=INK, outline="")
    c.create_oval(x + 2 * s, y + 1 * s, x + 4 * s, y + 3 * s, fill=INK, outline="")
    c.create_arc(x - 4 * s, y + 3 * s, x + 4 * s, y + 8 * s, start=200, extent=140, style="arc", outline=INK)


# ----------------------------------------------------------------------------
# Crops (used on the farm and as small icons)
# ----------------------------------------------------------------------------
def draw_crop(c, cx, by, name, fraction, ready, tick=0, k=1.0, sparkle=True):
    """Draw a plant standing at (cx, by). It grows taller and shows its produce as `fraction` goes to 1."""
    info = data.CROPS[name]
    colour = info["color"]
    shape = info["shape"]
    dark = GREEN
    light = LEAF
    bob = math.sin(tick * 0.35 + cx) * 1.6 * k if ready else 0

    if fraction <= 0.01 and not ready:              # just planted: a seed mound
        c.create_oval(cx - 11 * k, by - 9 * k, cx + 11 * k, by + 2 * k, fill="#6d4524", outline="")
        c.create_oval(cx - 2 * k, by - 7 * k, cx + 2 * k, by - 3 * k, fill="#d9c28f", outline="")
        return

    height = (14 + 32 * fraction) * k
    top = by - height + bob
    c.create_line(cx, by, cx, top, fill=dark, width=max(1, 3 * k))
    leaves = 2 + int(3 * fraction)
    for i in range(leaves):
        y = by - height * (i + 1) / (leaves + 1) + bob * (i + 1) / (leaves + 1)
        length = (6 + 9 * fraction) * k
        shade = light if i % 2 else dark
        if i % 2 == 0:
            c.create_oval(cx - 2 * k - length, y - 4 * k, cx - 2 * k, y + 3 * k, fill=shade, outline="")
        else:
            c.create_oval(cx + 2 * k, y - 4 * k, cx + 2 * k + length, y + 3 * k, fill=shade, outline="")

    if fraction < 0.7 and not ready:                # young plant: just a bud
        c.create_oval(cx - 3 * k, top - 3 * k, cx + 3 * k, top + 3 * k, fill=colour if fraction > 0.4 else "#8bd18b", outline="")
        return

    s = (1.0 if ready else 0.75) * k
    if shape == "round":                            # kamatis
        for dx, dy in ((-10, 8), (10, 10), (0, 0)):
            c.create_oval(cx + (dx - 7) * s, top + (dy - 7) * s, cx + (dx + 7) * s, top + (dy + 7) * s,
                          fill=colour, outline="#9f1d1d")
            c.create_oval(cx + (dx - 4) * s, top + (dy - 5) * s, cx + (dx - 1) * s, top + (dy - 2) * s, fill="#ff8a80", outline="")
    elif shape == "ear":                            # mais
        c.create_oval(cx + 3 * s, top + 4 * s, cx + 15 * s, top + 30 * s, fill="#7cb342", outline="")
        c.create_oval(cx + 6 * s, top + 6 * s, cx + 14 * s, top + 28 * s, fill=colour, outline="#c6a800")
        for j in range(4):
            c.create_line(cx + 7 * s, top + (10 + j * 5) * s, cx + 14 * s, top + (10 + j * 5) * s, fill="#c6a800")
    elif shape == "oval":                           # talong, ube, mangga
        edge = "#e65100" if name == "Mangga" else "#4a148c"
        for dx, dy in ((-11, 10), (9, 14), (-1, 4)):
            c.create_oval(cx + (dx - 6) * s, top + dy * s, cx + (dx + 6) * s, top + (dy + 18) * s, fill=colour, outline=edge)
            c.create_oval(cx + (dx - 3) * s, top + (dy + 2) * s, cx + dx * s, top + (dy + 7) * s, fill="#ffffff", outline="", stipple="gray50")
    elif shape == "stalk":                          # kangkong
        for dx in (-14, -7, 0, 7, 14):
            c.create_line(cx, top + 12 * s, cx + dx * s, top - 4 * s, fill=dark, width=max(1, 3 * k))
            c.create_oval(cx + (dx - 4) * s, top - 10 * s, cx + (dx + 4) * s, top - 2 * s, fill="#66bb6a" if ready else light, outline="")
    elif shape == "grain":                          # palay
        for dx in (-12, 0, 12):
            c.create_line(cx, top + 14 * s, cx + dx * s, top, fill="#c6a800", width=max(1, 2 * k))
            for j in range(4):
                c.create_oval(cx + (dx - 3 + j * 1.5) * s, top + (-3 + j * 5) * s, cx + (dx + 2 + j * 1.5) * s, top + (3 + j * 5) * s,
                              fill=colour, outline="#a8812c")
    else:                                           # saging
        for j in range(5):
            c.create_oval(cx + (3 + j * 3) * s, top + (10 + j * 5) * s, cx + (9 + j * 3) * s, top + (20 + j * 5) * s,
                          fill=colour, outline="#a68b00")
        c.create_oval(cx - 12 * s, top - 2 * s, cx - 2 * s, top + 10 * s, fill=light, outline="")
    if ready and sparkle and (tick // 3) % 2 == 0:
        c.create_line(cx + 18 * k, top - 6 * k, cx + 18 * k, top + 4 * k, fill="#fff59d", width=max(1, 2 * k))
        c.create_line(cx + 13 * k, top - 1 * k, cx + 23 * k, top - 1 * k, fill="#fff59d", width=max(1, 2 * k))


def crop_icon(c, x, y, name, k=0.8):
    """A fully grown crop used as a small picture (centre x, y)."""
    draw_crop(c, x, y + 22 * k, name, 1.0, True, 0, k, sparkle=False)
