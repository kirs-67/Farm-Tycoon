"""The three sorting algorithms required by the course, written by hand.

Nothing in this file uses Python's built-in sorting functions.

Where the game uses them (see FEATURE_MAP.md for the full map):
    bubble_sort     -> game.market_ranking()   ranks crops by today's price
    insertion_insert-> game.harvest()          puts each new crate in the Bodega in order
    selection_pick  -> game.soonest_plot()     finds the crop with the fewest days left

All functions accept:
    key      a function that returns the value to compare (default: the item itself)
    reverse  False = smallest first, True = largest first
    show     a function that turns an item into text (only used for the log)
    log      an optional list; when given, the algorithm appends step-by-step text
             to it. The "Algo Lab" tab in the game displays these lines.
"""


def _identity(item):
    return item


def _out_of_order(left_value, right_value, reverse):
    """True when the left value must move AFTER the right value.

    Equal values are NOT out of order, so the sorts are stable
    (items with equal keys keep their original order).
    """
    if reverse:
        return left_value < right_value
    return left_value > right_value


# ----------------------------------------------------------------------------
# BUBBLE SORT - repeated adjacent comparisons
# ----------------------------------------------------------------------------
def bubble_sort(items, key=None, reverse=False, show=None, log=None):
    """Return a new sorted list using Bubble Sort.

    Each pass walks through the list comparing neighbours (i and i + 1) and
    swapping them when they are in the wrong order. After pass 1 the largest
    value has "bubbled" to the end, after pass 2 the second largest, and so on.
    If a whole pass makes no swap, the list is already sorted and we stop early.
    """
    if key is None:
        key = _identity
    if show is None:
        show = str

    data = list(items)  # copy, so the caller's list is not changed
    size = len(data)
    if log is not None and size > 0:
        log.append("Start:  " + "  ".join(show(item) for item in data))

    for pass_number in range(size - 1):
        swapped = False
        # the last `pass_number` slots are already in their final place
        for i in range(size - 1 - pass_number):
            if _out_of_order(key(data[i]), key(data[i + 1]), reverse):
                data[i], data[i + 1] = data[i + 1], data[i]
                swapped = True
        if log is not None:
            log.append(f"Pass {pass_number + 1}: " + "  ".join(show(item) for item in data))
        if not swapped:
            break
    return data


# ----------------------------------------------------------------------------
# INSERTION SORT - insert one new item into an already ordered list
# ----------------------------------------------------------------------------
def insertion_insert(sorted_list, new_item, key=None, reverse=False, show=None, log=None):
    """Insert `new_item` into `sorted_list` (which is already in order), in place.

    The item is added at the end, then slid left past every neighbour that
    should come after it. Returns the final index of the new item.
    This single step is exactly what Insertion Sort repeats for every element.
    """
    if key is None:
        key = _identity
    if show is None:
        show = str

    sorted_list.append(new_item)
    position = len(sorted_list) - 1
    moves = 0
    while position > 0 and _out_of_order(key(sorted_list[position - 1]),
                                         key(sorted_list[position]), reverse):
        # swap the new item with the neighbour on its left
        sorted_list[position - 1], sorted_list[position] = (
            sorted_list[position], sorted_list[position - 1])
        position -= 1
        moves += 1

    if log is not None:
        log.append(f"Insert {show(new_item)}: slid past {moves} crate(s) -> slot {position + 1}")
    return position


def insertion_sort(items, key=None, reverse=False, show=None, log=None):
    """Return a new sorted list by inserting every item one at a time."""
    result = []
    for item in items:
        insertion_insert(result, item, key, reverse, show, log)
    return result


# ----------------------------------------------------------------------------
# SELECTION SORT - repeatedly select the smallest (or largest) remaining value
# ----------------------------------------------------------------------------
def selection_pick(items, key=None, largest=False, start=0, show=None, log=None):
    """Return the INDEX of the smallest (or largest) value from `start` onward.

    Returns -1 when there is nothing to choose from (empty / start too big).
    This "select the best remaining item" step is what Selection Sort repeats.
    """
    if key is None:
        key = _identity
    if show is None:
        show = str
    if start >= len(items):
        return -1

    best = start
    for i in range(start + 1, len(items)):
        if largest:
            better = key(items[i]) > key(items[best])
        else:
            better = key(items[i]) < key(items[best])
        if log is not None:
            log.append(f"Check {show(items[i])} vs best {show(items[best])}"
                       f" -> {'new best' if better else 'keep'}")
        if better:
            best = i
    if log is not None:
        log.append(f"Selected: {show(items[best])}")
    return best


def selection_sort(items, key=None, reverse=False, show=None, log=None):
    """Return a new sorted list using Selection Sort.

    For each position i, select the smallest remaining value (largest when
    reverse=True) from i to the end and swap it into position i.
    """
    data = list(items)
    for i in range(len(data) - 1):
        best = selection_pick(data, key, largest=reverse, start=i)
        if best != i:
            data[i], data[best] = data[best], data[i]
        if log is not None:
            shown = show if show is not None else str
            log.append(f"Step {i + 1}: " + "  ".join(shown(item) for item in data))
    return data
