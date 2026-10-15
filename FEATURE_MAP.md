# Feature Map: where each required concept appears

Search for the **function name** in the file (line numbers shift as code changes).

| Concept | Defined in | Called / used in | What it does in the game | How to see it while playing |
|---|---|---|---|---|
| **Bubble Sort** | `algorithms.py` → `bubble_sort()` | `game.py` → `market_ranking()` ← called by `ui.py` → `refresh()` (every screen update) | Ranks all discovered crops by **today's selling price**, highest first. Runs every time the screen refreshes. | **Market** tab (chart icon: medals 1, 2, 3 and the price bars) and **Algo Lab** (flask tab, pass-by-pass log) |
| **Insertion Sort** | `algorithms.py` → `insertion_insert()` (and `insertion_sort()`) | `game.py` → `harvest()` | Every harvested crate is inserted into the **already-ordered Bodega** (highest worth first). The crate slides left past cheaper crates. | Harvest a crop → **Bodega** tab (crate icon: crates stay ordered, best first); **Algo Lab** shows how many crates it slid past |
| **Selection Sort** | `algorithms.py` → `selection_pick()` (and `selection_sort()`) | `game.py` → `soonest_plot()` and `sell_best()` | `soonest_plot()` **selects the crop with the lowest remaining growth time** ("Next Up"). `sell_best()` **selects the crate with the highest price today**. | Press **N** or the target button (cyan outline on the soonest crop), or **S** (sells best crate); **Algo Lab** shows each comparison |
| **Tuple** | `zones.py` (cell coordinates), `data.py` (`FIELDS`, `BEDS`, `DIFFICULTIES` pairs) | `game.py` → `self.plots` keys `(row, col)`; `market_ranking()` items `(crop, price)`; `soonest_plot()` returns `(cell, days_left)`; `ui.py` → `cell_box()` | Fixed groups of values: plot coordinates, field column ranges, ranking pairs. | Hover a plot: the Algo Lab shows `plot under mouse (tuple)` |
| **Set** | `game.py` → `new_game()` | `self.discovered`, `self.achievements`, `self.owned_fields`, `self.upgrades`; `discover()`, `unlock()`, `buy_field()`, `buy_upgrade()` | Unique things with no duplicates: discovered crop varieties, unlocked achievements, owned fields, bought upgrades. A crop must be in `discovered` before it can be planted. | **Journal** tab (book icon: crop stickers and medals); Mystery Seed Packet in **Shop** adds to the set |
| **Dictionary** | `data.py` → `CROPS`, `QUALITY`, `UPGRADES`, `EVENTS`, `ACHIEVEMENTS`, `DIFFICULTIES` | `game.py` → `self.plots`, `self.index` (price multiplier per crop), `crop_counts()` (quantities), `pick_event()` (weighted events) | Stores prices, growth times, seed costs, quantities and plot state by key. | **Market** (prices), **Bodega** (quantities line), **Algo Lab** (`crates by crop`, `price index`) |
| **Recursion** | `zones.py` → `collect_cells()`, `sum_values()`, `tree_report()` | `game.py` → `harvest_zone()`, `harvest_all()`, `ready_count()`, `ready_value()`; `ui.py` → `harvest_field_action()`, `refresh_lab()` | Walks the **nested farm** (Farm → Field → Bed → plots) to find every ready plot and total its harvest value. **Base case:** a zone with no child zones. **Progress:** every call goes one level deeper. | Click a **field name bar** (basket badge) or press **H**; **Algo Lab** prints the indented zone report |

## Details to cite in the defense

**Farm tree used by the recursion**

```
Bukid (root)
├── Bahay Kubo Field ── Upper bed (4 plots), Lower bed (4 plots)
├── Ilog Field       ── Upper bed (4 plots), Lower bed (4 plots)
└── Burol Field      ── Upper bed (4 plots), Lower bed (4 plots)
```

**Base case:** `if not node["children"]: return found`: a bed has no children, so recursion stops.
**Recursive case:** `found += collect_cells(child, test)` for each child zone.

**No built-in sorting:** the project never calls `sorted()` or `.sort()`. A unit test (`NoBuiltInSortTests`) scans every `.py` file in the project root to prove it.

**Smart click (game.py → `smart_action`)** decides whether a click plants, waters or harvests, using the plot dictionary and tuple keys.

**Sorts are real gameplay, not demos:** deleting `bubble_sort` breaks the Market board; deleting `insertion_insert` breaks harvesting; deleting `selection_pick` breaks "Next Up" and "Sell Best".

## Where each sort is tested (empty, one item, short game list)

| Sort | Test class in `tests/test_algorithms.py` |
|---|---|
| Bubble | `BubbleSortTests` (`test_empty_list`, `test_one_item`, `test_game_data_*`) |
| Insertion | `InsertionSortTests` (`test_insert_into_empty_list`, `test_insert_one_item_list`, `test_insert_keeps_descending_order`) |
| Selection | `SelectionSortTests` (`test_pick_from_empty_list`, `test_pick_from_one_item`, `test_pick_smallest/largest`) |
