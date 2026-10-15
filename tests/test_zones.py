"""Tests for the recursive functions in zones.py."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import data  # noqa: E402
import zones  # noqa: E402


class FarmTreeTests(unittest.TestCase):
    def setUp(self):
        self.tree = zones.build_farm_tree()

    def test_tree_shape(self):
        self.assertEqual(len(self.tree["children"]), 3)
        for field in self.tree["children"]:
            self.assertEqual(len(field["children"]), 2)

    def test_every_plot_appears_exactly_once(self):
        cells = zones.collect_cells(self.tree, lambda cell: True)
        self.assertEqual(len(cells), data.GRID_ROWS * data.GRID_COLS)
        self.assertEqual(len(set(cells)), len(cells))

    def test_cells_are_tuples(self):
        for cell in zones.collect_cells(self.tree, lambda cell: True):
            self.assertIsInstance(cell, tuple)

    def test_field_of(self):
        self.assertEqual(zones.field_of((0, 0)), 0)
        self.assertEqual(zones.field_of((3, 3)), 1)
        self.assertEqual(zones.field_of((2, 5)), 2)
        self.assertEqual(zones.field_of((0, 99)), -1)


class RecursionTests(unittest.TestCase):
    def test_base_case_single_leaf(self):
        leaf = zones.make_node("Bed", cells=[(0, 0), (0, 1)])
        self.assertEqual(zones.collect_cells(leaf, lambda cell: cell[1] == 1), [(0, 1)])

    def test_empty_zone(self):
        empty = zones.make_node("Empty")
        self.assertEqual(zones.collect_cells(empty, lambda cell: True), [])
        self.assertEqual(zones.sum_values(empty, lambda cell: 5), 0)

    def test_recursion_reaches_deep_cells(self):
        deep = zones.make_node("A", children=[zones.make_node("B", children=[
            zones.make_node("C", cells=[(1, 1)])])])
        self.assertEqual(zones.collect_cells(deep, lambda cell: True), [(1, 1)])

    def test_sum_values(self):
        tree = zones.build_farm_tree()
        self.assertEqual(zones.sum_values(tree, lambda cell: 1), 24)
        field = tree["children"][0]
        self.assertEqual(zones.sum_values(field, lambda cell: 2), 16)

    def test_tree_report_counts_match(self):
        tree = zones.build_farm_tree()
        count, lines = zones.tree_report(tree, lambda cell: cell[0] == 0)
        self.assertEqual(count, data.GRID_COLS)
        self.assertTrue(lines[0].startswith("Bukid"))
        self.assertEqual(len(lines), 1 + 3 + 6)


if __name__ == "__main__":
    unittest.main()
