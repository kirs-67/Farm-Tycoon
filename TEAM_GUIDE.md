# Team Guide: roles, GitHub plan, live demo and defense

> The exam gives every student **30 individual points** for their code contribution and their explanation. You cannot get those points from the repository alone. **Every member must read their own part, run it, change one small thing in it, and be able to explain it without looking at notes.** This guide is built to make that fast.

---

## 1. Suggested role split (edit it so it matches who really does what)

| Role | Owns these files / functions | "Explain it" topic (8 pts) | Concept link |
|---|---|---|---|
| **Team coordinator and integrator** | `main.py`; `game.py`: `new_game`, `end_day`, `run_event`, `pick_event` | How one day passes: growth, price drift, random event, fiesta, game over | Dictionary (`EVENTS` weights, `self.index`) |
| **Gameplay programmer** | `game.py`: `plant`, `water`, `rush`, `harvest` (rules part), `sell_crate`, `sell_all`, `buy_field`, `buy_upgrade`, `check_win`, `rank` | The core loop and the win/loss conditions | Tuple (plot keys), Dictionary (plots) |
| **Data structures and algorithms programmer** | `algorithms.py` (all three sorts); `zones.py` (all recursion); `game.py`: `market_ranking`, `soonest_plot`, `sell_best`, the `insertion_insert` call in `harvest` | Trace each sort and the recursion base case | Bubble, Insertion, Selection, Recursion |
| **Interface and asset designer** | `ui.py`: screens, `draw_farm`, `draw_plot`, panel tabs, `click_plot`, `run`; `icons.py` (all pictures); `sounds.py` (sound effects) | How a click becomes a game action, a sound and a new picture | Tuple (`cell_box`), connects every concept to the player |
| **QA, documentation and release lead** | `tests/`, `tools/`, `README.md`, `FEATURE_MAP.md`, `TESTING.md`, GitHub repo; code feature: achievements (`unlock`, `ACHIEVEMENTS`, Journal tab) and `discover` | The test plan, one bug fixed, and the set of achievements/discoveries | Set |

**4-person team:** merge QA/docs/release into the coordinator and split the algorithm work: one person takes Bubble + Selection, another takes Insertion + Recursion.

## 2. GitHub plan (a real commit history matters)

Do **not** upload everything in one commit. Each member should commit **their own files from their own account**. Suggested order (adapt it to what each person really does):

```bash
# coordinator creates the repo, adds everyone as collaborators, and the instructor (private repo)
git clone <repo-url>
```

| Step | Who | Commit message idea |
|---|---|---|
| 1 | Coordinator | `Add project skeleton, main.py and .gitignore` |
| 2 | DSA programmer | `Add Bubble Sort in algorithms.py` / `Add Insertion Sort` / `Add Selection Sort` (three commits) |
| 3 | DSA programmer | `Add farm tree and recursive collect_cells / sum_values in zones.py` |
| 4 | Coordinator + Gameplay | `Add data.py with crops, prices and events` |
| 5 | Gameplay | `Add plant, water and harvest rules` / `Add selling and win/loss` / `Add shop and upgrades` |
| 6 | Coordinator | `Add day cycle and random events` |
| 7 | Interface | `Add start screen and farm drawing` / `Add tabs and controls` / `Add end screen` |
| 8 | QA | `Add unit tests for sorting algorithms` / `Add game rule tests` / `Add balance simulator` |
| 9 | QA | `Add README, feature map and testing notes` |
| 10 | Everyone | One small bug fix each, with a clear message |

Before the exam: **clone into a clean folder**, follow the README, run `python main.py`, run the tests. If the repo is private, add the instructor as a collaborator.

## 3. Live demonstration script (about 5 minutes)

1. **Coordinator (30 s):** "Our game is Bukid Tycoon, a Tkinter farm tycoon. The goal is to earn P__ in 30 days." Start on **Easy** so a win is likely.
2. **Gameplay (60 s):** pick a seed, click plots to plant, click again to water, end days (`Space`), harvest (`H`), sell (`S`). Mention the sounds and the drag-to-paint. Point at coins and day counters (feedback).
3. **DSA (90 s):** open the **Algo Lab** tab (flask icon). Show the bubble sort passes (Market ranking), the insertion step (new crate slid into the Bodega), press **N** and show the selection step, point at the recursion report. Say the base case.
4. **Interface (30 s):** show the events (rain, typhoon), fiesta day, locked fields, the shop.
5. **QA (45 s):** show `python -m unittest discover -s tests -v` passing (112 tests), then the empty / one-item / short-list sort tests.
6. **Ending (30 s):** reach the goal for the victory screen, press **Play Again**, then **Exit**. (Optionally show a loss with **Hard**.)

Everyone then answers questions about their own feature **and** the overall flow.

## 4. Trace examples (the instructor may ask for one)

### Bubble Sort: ranking three crops by price (highest first)

`[("Kangkong",12), ("Mais",25), ("Kamatis",34)]`

* Pass 1: compare Kangkong(12) vs Mais(25). 12 < 25 so swap. Compare Kangkong(12) vs Kamatis(34). Swap. Result: Mais, Kamatis, Kangkong.
* Pass 2: compare Mais(25) vs Kamatis(34). Swap. Result: Kamatis, Mais, Kangkong.
* Pass 3: no swaps, so the list is sorted and the loop stops early (`swapped = False`).

(You can watch exactly this in the **Algo Lab** tab.)

### Insertion Sort: crate worth 35 enters Bodega `[45, 28, 12]`

* Append at the end: `[45, 28, 12, 35]`, position 3.
* Left neighbour 12 < 35 so swap: `[45, 28, 35, 12]`, position 2.
* Left neighbour 28 < 35 so swap: `[45, 35, 28, 12]`, position 1.
* Left neighbour 45 >= 35, so stop. The new crate "slid past 2 crates".

### Selection Sort: "Next Up"

Growing crops as `(cell, days_left)`: `[((0,0), 3), ((0,1), 2), ((1,0), 3)]`.
Start with best = index 0 (3 days). Check index 1: 2 < 3, so best = 1. Check index 2: 3 < 2? No. **Selected: index 1, plot (0,1), 2 days.**

### Recursion: `collect_cells(Bahay Kubo Field, is_ready)`

1. The field has no cells of its own but has 2 child beds, so it is **not** the base case.
2. It calls `collect_cells(Upper bed)`. The bed has **no children**, so it is the **base case**: it returns its ready plots.
3. It calls `collect_cells(Lower bed)`: the same.
4. The field joins both answers into one list. Each call works on a smaller part of the tree, so it must stop.

## 5. Likely questions and short answers

**Sorting**

* *Why did you write your own sort?* The exam says built-in `sort()` / `sorted()` does not count. A test scans the code to prove we never use them.
* *Which sort is used where, and why that sort?* Bubble: ranking (market board). Insertion: Bodega, because the list is always already ordered and only one new item arrives. Selection: finding one best item (soonest crop, best crate).
* *What is the time complexity?* Bubble O(n²) (best case O(n) with the early stop), Insertion O(n) per insert, Selection O(n) per pick. Our lists have at most 24 items.
* *Is your Bubble Sort stable?* Yes: it only swaps when left > right (strictly), so equal items keep their order.
* *What is `key` and `reverse`?* `key` tells the sort which value to compare (for example the price in a tuple); `reverse=True` means highest first.
* *What does the early stop do?* If a full pass makes no swap the list is sorted, so we `break`.

**Tuple, set, dictionary**

* *Why are plot coordinates tuples?* They never change and they work as dictionary keys (`self.plots[(row, col)]`). A list cannot be a key.
* *Why a set for discovered crops?* Duplicates are impossible, and `crop in self.discovered` is the check that allows planting.
* *Show a dictionary in use.* `data.CROPS["Mais"]["price"]` gives the base price; `self.index["Mais"]` is today's multiplier; `crop_counts()` builds `{crop: quantity}`.

**Recursion**

* *What is the base case?* A zone with no children (a bed): `if not node["children"]: return found`.
* *How does it make progress?* Each call receives a child zone, one level deeper in the farm tree.
* *Is your animation recursive?* No. The animation uses Tkinter's `after()` timer, which is the normal event loop. Recursion is only in `zones.py`.
* *What could break it?* A tree that contains itself (a cycle). Ours is a fixed three-level tree, so it always ends.

**Whole game**

* *Walk me through one day.* `end_day()`: plants grow (and count watered days), prices drift toward normal with randomness, a random event may fire, fiesta check, then the UI refreshes.
* *How does quality work?* Watered share of days = `watered_days / grow`. At 80% or more you get the best odds of Premium; below 50% mostly Normal.
* *Where is the win/loss?* `check_win()` (goal reached after a sale) and the end of `end_day()` on day 30.
* *How does one click know what to do?* `FarmGame.smart_action(cell, crop)`: empty plot means plant, ready means harvest, thirsty means water. The plot is found by its `(row, col)` tuple.
* *How does the sound work without audio files?* `sounds.py` builds waves with `math.sin` and writes .wav files to a temp folder; Windows plays them with `winsound`. No sound hardware means silence, never a crash.
* *How do you separate rules from the screen?* `game.py` has no Tkinter and is unit-tested; `ui.py` only draws and calls `game.py`.
* *What would you add next?* Saving a high-score table (a leaderboard kept in order with Insertion Sort), more crops, sound.

## 6. Quick personal checklist (tick before Thursday)

- [ ] I can launch the game from a clean clone.
- [ ] I can point to my files and functions in under 10 seconds.
- [ ] I can explain my feature in 2 minutes and name the course concept it uses.
- [ ] I can trace one example by hand (sort step or recursion).
- [ ] I changed one tiny thing in my code (for example a price in `data.py`) and saw the result.
- [ ] I know the overall flow: start screen, plant, water, end day, harvest, sell, win/loss, restart.
- [ ] My commits appear in the GitHub history under my own account.
