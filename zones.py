"""The farm as a tree of zones, plus the RECURSIVE functions that walk it.

    Bukid (whole farm)
    |-- Bahay Kubo Field
    |   |-- Upper bed  (4 plots)
    |   `-- Lower bed  (4 plots)
    |-- Ilog Field   ... (same shape)
    `-- Burol Field  ... (same shape)

A zone ("node") is a dictionary:
    {"name": str, "cells": [(row, col), ...], "children": [node, ...]}
`cells` are TUPLES - the coordinates of the plots that belong directly to the zone.
"""

from data import BEDS, FIELDS


def make_node(name, cells=None, children=None):
    return {"name": name, "cells": cells or [], "children": children or []}


def build_farm_tree():
    """Build the nested farm: Farm -> Fields -> Beds -> plot coordinates."""
    farm = make_node("Bukid")
    for field in FIELDS:
        first_col, last_col = field["cols"]
        field_node = make_node(field["name"])
        for bed_name, (first_row, last_row) in BEDS:
            cells = [(row, col)
                     for row in range(first_row, last_row + 1)
                     for col in range(first_col, last_col + 1)]
            field_node["children"].append(make_node(f"{field['name']} - {bed_name}", cells=cells))
        farm["children"].append(field_node)
    return farm


def field_of(cell):
    """Return the index of the field that owns a (row, col) tuple."""
    column = cell[1]
    for index, field in enumerate(FIELDS):
        first_col, last_col = field["cols"]
        if first_col <= column <= last_col:
            return index
    return -1


# ----------------------------------------------------------------------------
# RECURSION
# ----------------------------------------------------------------------------
def collect_cells(node, test):
    """Return every plot (in this zone AND all zones nested inside it) where test(cell) is True.

    Base case:      a zone with no children -> return only its own matching cells.
    Recursive case: ask every child zone the same question and join the answers.
    Each call works on a smaller part of the tree, so it always reaches the base case.
    """
    found = [cell for cell in node["cells"] if test(cell)]
    if not node["children"]:           # BASE CASE
        return found
    for child in node["children"]:
        found += collect_cells(child, test)   # RECURSIVE CASE
    return found


def sum_values(node, value_of):
    """Add up value_of(cell) for every plot in this zone and everything nested in it."""
    total = sum(value_of(cell) for cell in node["cells"])
    if not node["children"]:           # BASE CASE
        return total
    for child in node["children"]:
        total += sum_values(child, value_of)  # RECURSIVE CASE
    return total


def tree_report(node, test, depth=0):
    """Return (count, lines): how many plots pass `test`, and an indented text report.

    Used by the "Algo Lab" tab so the class can SEE the recursion working.
    """
    count = sum(1 for cell in node["cells"] if test(cell))
    if not node["children"]:           # BASE CASE
        return count, ["    " * depth + f"{node['name']}: {count}"]
    child_lines = []
    for child in node["children"]:
        child_count, lines = tree_report(child, test, depth + 1)   # RECURSIVE CASE
        count += child_count
        child_lines += lines
    return count, ["    " * depth + f"{node['name']}: {count}"] + child_lines
