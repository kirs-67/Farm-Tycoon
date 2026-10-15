# Testing

## How to run

```bash
python -m unittest discover -s tests -v     # 112 automated tests, a couple of seconds
python tools/simulate.py 200                 # balance: bots play 200 full seasons
xvfb-run -a python tools/ui_smoke.py shots   # (Linux) plays a season in the real window + screenshots
```

## Automated tests (112)

| File | Tests | What is covered |
|---|---|---|
| `tests/test_algorithms.py` | 26 | Each sort with an **empty list**, a **one-item list** and a **short game-data list**; ascending and descending; stability (equal values keep order); original list not changed; results verified (ordered and same items) on 10+ lists; a check that no source file uses Python's built-in sorting |
| `tests/test_zones.py` | 9 | Farm tree shape, every plot appears exactly once, tuple coordinates, recursion base case (leaf, empty zone), deep nesting, totals |
| `tests/test_sounds.py` | 8 | All 19 sound effects are generated as valid .wav files, mute works, unknown sounds are ignored, a broken or missing speaker never crashes the game |
| `tests/test_game.py` | 69 | Planting rules, watering, growth, harvesting, ordered Bodega, full Bodega, selling and price drops, fiesta bonus, ranking, "Next Up", shop and upgrades, set uniqueness, all 7 random events, win, loss, restart, difficulty, game-over blocking, the one-click "smart action" (plant / water / harvest) |

## Manual test plan (normal play)

The "Auto-checked" column was verified by `tools/ui_smoke.py` (clicks the real on-screen buttons) and the unit tests. **Each member should also play through it by hand on their own computer and tick the last column before the exam.**

| # | Scenario | Expected result | Auto-checked | Team ticked by hand |
|---|---|---|---|---|
| 1 | Launch with `python main.py` | Start screen with title, instructions, controls, difficulty | Pass (smoke test / unit tests) | [ ] |
| 2 | Press START GAME | Farm appears, Day 1, P150 | Pass (smoke test / unit tests) | [ ] |
| 3 | Pick Mais, click 6 plots (or drag across them) | Coins drop, sprouts appear, growth dots show the days | Pass (smoke test / unit tests) | [ ] |
| 4 | Click a locked plot | Friendly message, no crash | Pass (smoke test / unit tests) | [ ] |
| 5 | Plant on an occupied plot | Message "already planted", coins unchanged | Pass (smoke test / unit tests) | [ ] |
| 6 | Water All (A), End Day (Space) x3 | Crops grow, plots glow gold with a basket | Pass (smoke test / unit tests) | [ ] |
| 7 | Harvest All (H) | Crates appear in Bodega in order of worth | Pass (smoke test / unit tests) | [ ] |
| 8 | Bodega full | Harvest blocked with a message | Pass (smoke test / unit tests) | [ ] |
| 9 | Sell Best (S), Sell All | Coins rise, that crop's price falls | Pass (smoke test / unit tests) | [ ] |
| 10 | Buy field / upgrades / packet | Coins spent, new plots/benefit/new crop | Pass (smoke test / unit tests) | [ ] |
| 11 | Reach goal | Victory screen with rank and stats | Pass (smoke test / unit tests) | [ ] |
| 12 | Reach Day 30 below goal | "Season Over" screen | Pass (smoke test / unit tests) | [ ] |
| 13 | Play Again / Main Menu / Exit | New game / menu / window closes | Pass (smoke test / unit tests) | [ ] |
| 14 | Mash every key and button during play | No crash, no dead controls |
| 14b | Press M, then play | Sound turns off and on; with sound on, each action has its own sound | Pass (smoke test / unit tests) | [ ] |
| 15 | Each random event (rain, typhoon, pests, glut, demand, gift, seed swap) | Matching message, visual effect and state change | Pass (smoke test / unit tests) | [ ] |

## Balance results (`tools/simulate.py`)

A simple bot (it floods the market and ignores the Storm Shield) plays full seasons with random events on:

| Bot | Easy (P1,500) | Normal (P3,000) |
|---|---|---|
| Idle (does nothing) | 0% wins | 0% wins |
| Casual (no upgrades, waters every 2nd day) | about 49% | about 24% |
| Good (expands, upgrades, waters daily) | about 77% | about 61% |

A thinking human who mixes crops and uses upgrades should beat these bots.

## Bug log

| # | Bug found | Cause | Fix |
|---|---|---|---|
| 1 | 10 unit tests failed on first run | Test setup planted Palay, which is undiscovered at the start | Used a starter crop (Mais) in those tests |
| 2 | Harvest tests failed randomly | Random events (pests, typhoon) destroyed crops mid-test | Added `FarmGame(events=False)` switch; tests use it |
| 3 | "No built-in sort" test failed | A docstring mentioned `sorted()` | Reworded the docstring |
| 4 | Farm picture lagged behind clicks | The canvas only redrew on the animation timer | `refresh()` now redraws the farm immediately |
| 5 | END DAY button was cut off | Tool row was wider than the window | Moved END DAY to the seed row |
| 6 | Menu button clipped on fiesta days | Long event text made the top bar taller | Event text now sits in a fixed-size box; fiesta text shortened |
| 7 | Window too tall for 768-pixel screens | Notebook tabs requested more height than the farm | Smaller plots and tab content; window sizes itself to fit (about 700 px) |
| 8 | Event banner hid the typhoon / rain name on fiesta days | Fiesta overwrote the event text | Fiesta text now includes the other event |
| 9 | Menu sun hid the title; Bodega tab did not redraw instantly; medal banner overlapped its icon (new picture interface) | Overlay used the farm sun position; panel only redrew on the timer | Sun moved; tab clicks redraw at once; banner re-laid out |
