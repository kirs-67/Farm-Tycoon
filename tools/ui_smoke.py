"""Headless smoke test for the interface (needs a display, e.g. xvfb-run).

    xvfb-run -a python tools/ui_smoke.py [screenshot_folder]

It opens the real window, clicks the real on-screen buttons and plots, drags across plots, plays a whole
season to the end screen, and fails loudly if anything raises an error.
"""
import os
import subprocess
import sys
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import data  # noqa: E402
import sounds  # noqa: E402
import ui  # noqa: E402

SHOTS = sys.argv[1] if len(sys.argv) > 1 else None
SURFACES = {"hud": "hud", "panel": "panel", "dock": "dock", "overlay": "overlay"}


def snap(root, name):
    for _ in range(3):
        root.update()
    if SHOTS:
        os.makedirs(SHOTS, exist_ok=True)
        subprocess.run(["import", "-window", "root", os.path.join(SHOTS, name + ".png")], check=False)


def press(app, surface, hid):
    """Click the on-screen button with this id, exactly like a player would."""
    app.draw_all()
    hit = app.find_hit(surface, hid)
    assert hit is not None, "no button " + surface + ":" + hid
    x1, y1, x2, y2 = hit["box"]
    getattr(app, SURFACES[surface]).event_generate("<Button-1>", x=int((x1 + x2) / 2), y=int((y1 + y2) / 2))
    app.root.update()


def click_cell(app, cell):
    x1, y1, x2, y2 = ui.cell_box(cell)
    app.farm.event_generate("<Button-1>", x=(x1 + x2) // 2, y=(y1 + y2) // 2)
    app.root.update()


def key(app, name):
    app.root.event_generate("<Key>", keysym=name)
    app.root.update()


def main():
    errors = []
    root = tk.Tk()
    root.report_callback_exception = lambda *info: errors.append(info)
    played = []
    app = ui.BukidApp(root, sound=sounds.SoundBoard(player=played.append))
    root.update()
    print("window size:", root.winfo_width(), "x", root.winfo_height())
    snap(root, "1_menu")

    press(app, "overlay", "help")
    snap(root, "2_help")
    press(app, "overlay", "close")
    press(app, "overlay", "diff:Easy")
    assert app.difficulty == "Easy"
    press(app, "overlay", "start")
    assert app.mode == "play" and app.game.goal == data.DIFFICULTIES["Easy"]

    # plant with single clicks, water with a click, and paint with a drag
    press(app, "dock", "seed:Mais")
    for cell in [(0, 0), (0, 1), (1, 0)]:
        click_cell(app, cell)
    assert app.game.plots[(0, 0)]["crop"] == "Mais"
    click_cell(app, (0, 0))                     # second click waters it
    assert app.game.plots[(0, 0)]["watered_today"]
    press(app, "dock", "seed:Kamatis")
    x1, y1, x2, y2 = ui.cell_box((1, 1))
    app.farm.event_generate("<Button-1>", x=x1 + 10, y=y1 + 10)
    start = ui.cell_box((2, 0))
    app.farm.event_generate("<B1-Motion>", x=start[0] + 10, y=start[1] + 10)
    end = ui.cell_box((2, 1))
    app.farm.event_generate("<B1-Motion>", x=end[0] + 10, y=end[1] + 10)
    root.update()
    assert app.game.plots[(2, 0)] is not None and app.game.plots[(2, 1)] is not None, "drag should plant"
    click_cell(app, (0, 5))                     # locked: friendly message
    press(app, "dock", "water_all")
    press(app, "dock", "next")
    assert app.highlight is not None
    app.farm.event_generate("<Motion>", x=100, y=200)
    snap(root, "3_planted")

    for _ in range(3):
        press(app, "dock", "end_day")
        press(app, "dock", "water_all")
    snap(root, "4_ready")
    press(app, "dock", "harvest_all")
    assert len(app.game.bodega) > 0
    press(app, "panel", "tab:bodega")
    snap(root, "5_bodega")
    press(app, "panel", "crate:0")
    press(app, "panel", "sell_best")
    press(app, "panel", "tab:lab")
    snap(root, "6_lab")
    press(app, "panel", "tab:shop")
    app.game.coins = 2000
    app.refresh()
    snap(root, "7_shop")
    for card in ("field1", "field2", "Irrigation", "Bodega", "Storm Shield", "Scarecrow", "packet", "packet", "packet", "packet", "packet"):
        press(app, "panel", "buy:" + card)
    snap(root, "8_after_shop")
    press(app, "panel", "tab:journal")
    snap(root, "9_journal")
    press(app, "panel", "tab:market")
    press(app, "dock", "boost")
    click_cell(app, (3, 0))
    press(app, "dock", "boost")
    press(app, "hud", "sound")
    press(app, "hud", "sound")
    snap(root, "10_market")

    for name in list(data.EVENTS):               # every event: drawing and sound must not crash
        app.game.run_event(name)
        app.refresh()
        snap(root, "event_" + name) if name in ("rain", "typhoon", "pests") else root.update()
    app.game.day = 9
    app.end_day()
    snap(root, "11_fiesta")
    press(app, "dock", "sell_all")
    while not app.game.over:
        key(app, "a")
        key(app, "h")
        key(app, "s")
        key(app, "space")
    for _ in range(12):
        root.update()
        root.after(60)
    snap(root, "12_end")
    assert app.mode == "end", app.mode
    press(app, "overlay", "again")
    assert app.mode == "play" and app.game.day == 1
    press(app, "hud", "menu")
    assert app.mode == "menu"
    assert len(played) > 20, "sound effects should have been requested"
    root.destroy()
    if errors:
        raise SystemExit("UI errors: " + repr(errors[:3]))
    print("UI smoke test passed.", len(played), "sounds requested.")


if __name__ == "__main__":
    main()
