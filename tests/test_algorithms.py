"""Tests for the three hand-written sorting algorithms.

Each sort is tested with: an empty list, a one-item list, and a short game-data list
(crops with prices), as the exam guide requires.
Run all tests from the project folder:   python -m unittest discover -s tests -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import algorithms  # noqa: E402

CROPS = [("Mais", 28), ("Mangga", 270), ("Kangkong", 12), ("Palay", 85), ("Kamatis", 36)]


def price(pair):
    return pair[1]


def is_in_order_same_items(result, original):
    """True if `result` is in ascending order and holds exactly the same items as `original`."""
    if len(result) != len(original):
        return False
    for i in range(len(result) - 1):
        if result[i] > result[i + 1]:
            return False
    counts = {}
    for item in original:
        counts[item] = counts.get(item, 0) + 1
    for item in result:
        counts[item] = counts.get(item, 0) - 1
    return all(value == 0 for value in counts.values())


class BubbleSortTests(unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual(algorithms.bubble_sort([]), [])

    def test_one_item(self):
        self.assertEqual(algorithms.bubble_sort([("Mais", 28)], key=price), [("Mais", 28)])

    def test_game_data_high_to_low(self):
        result = algorithms.bubble_sort(CROPS, key=price, reverse=True)
        self.assertEqual([name for name, _ in result],
                         ["Mangga", "Palay", "Kamatis", "Mais", "Kangkong"])

    def test_game_data_low_to_high(self):
        result = algorithms.bubble_sort(CROPS, key=price)
        self.assertEqual([cost for _, cost in result], [12, 28, 36, 85, 270])

    def test_does_not_change_original_list(self):
        original = list(CROPS)
        algorithms.bubble_sort(CROPS, key=price)
        self.assertEqual(CROPS, original)

    def test_equal_values_keep_order(self):
        items = [("a", 5), ("b", 5), ("c", 5)]
        self.assertEqual(algorithms.bubble_sort(items, key=price), items)

    def test_sorts_many_lists_correctly(self):
        for size in range(0, 12):
            numbers = [(size * 7 + i * 13) % 11 for i in range(size)]
            self.assertTrue(is_in_order_same_items(algorithms.bubble_sort(numbers), numbers))

    def test_log_records_steps(self):
        steps = []
        algorithms.bubble_sort([3, 1, 2], log=steps)
        self.assertTrue(steps[0].startswith("Start"))
        self.assertGreater(len(steps), 1)


class InsertionSortTests(unittest.TestCase):
    def test_insert_into_empty_list(self):
        shelf = []
        position = algorithms.insertion_insert(shelf, 5)
        self.assertEqual(shelf, [5])
        self.assertEqual(position, 0)

    def test_insert_one_item_list(self):
        shelf = [10]
        algorithms.insertion_insert(shelf, 4)
        self.assertEqual(shelf, [4, 10])

    def test_insert_keeps_descending_order(self):
        shelf = []
        for crop in CROPS:
            algorithms.insertion_insert(shelf, crop, key=price, reverse=True)
        self.assertEqual([name for name, _ in shelf],
                         ["Mangga", "Palay", "Kamatis", "Mais", "Kangkong"])

    def test_insert_returns_final_position(self):
        shelf = [("Mangga", 270), ("Palay", 85), ("Kangkong", 12)]
        position = algorithms.insertion_insert(shelf, ("Mais", 28), key=price, reverse=True)
        self.assertEqual(position, 2)

    def test_equal_value_goes_after_existing(self):
        shelf = [("a", 5)]
        algorithms.insertion_insert(shelf, ("b", 5), key=price, reverse=True)
        self.assertEqual([name for name, _ in shelf], ["a", "b"])

    def test_insertion_sort_empty_and_single(self):
        self.assertEqual(algorithms.insertion_sort([]), [])
        self.assertEqual(algorithms.insertion_sort([7]), [7])

    def test_insertion_sort_many_lists(self):
        for size in range(0, 12):
            numbers = [(size * 5 + i * 17) % 13 for i in range(size)]
            self.assertTrue(is_in_order_same_items(algorithms.insertion_sort(numbers), numbers))


class SelectionSortTests(unittest.TestCase):
    def test_pick_from_empty_list(self):
        self.assertEqual(algorithms.selection_pick([]), -1)

    def test_pick_from_one_item(self):
        self.assertEqual(algorithms.selection_pick([("Mais", 28)], key=price), 0)

    def test_pick_smallest(self):
        index = algorithms.selection_pick(CROPS, key=price)
        self.assertEqual(CROPS[index], ("Kangkong", 12))

    def test_pick_largest(self):
        index = algorithms.selection_pick(CROPS, key=price, largest=True)
        self.assertEqual(CROPS[index], ("Mangga", 270))

    def test_pick_with_start_position(self):
        index = algorithms.selection_pick([1, 9, 3, 2], start=2)
        self.assertEqual(index, 3)

    def test_pick_start_past_end(self):
        self.assertEqual(algorithms.selection_pick([1, 2], start=5), -1)

    def test_tie_picks_first(self):
        self.assertEqual(algorithms.selection_pick([("a", 1), ("b", 1)], key=price), 0)

    def test_selection_sort_empty_and_single(self):
        self.assertEqual(algorithms.selection_sort([]), [])
        self.assertEqual(algorithms.selection_sort([3]), [3])

    def test_selection_sort_game_data(self):
        result = algorithms.selection_sort(CROPS, key=price, reverse=True)
        self.assertEqual([cost for _, cost in result], [270, 85, 36, 28, 12])

    def test_selection_sort_many_lists(self):
        for size in range(0, 12):
            numbers = [(size * 3 + i * 19) % 14 for i in range(size)]
            self.assertTrue(is_in_order_same_items(algorithms.selection_sort(numbers), numbers))


class NoBuiltInSortTests(unittest.TestCase):
    """The exam says built-in sorting does not count. Make sure we never use it."""

    def test_source_files_do_not_call_builtin_sort(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for name in os.listdir(root):
            if name.endswith(".py"):
                with open(os.path.join(root, name), encoding="utf-8") as handle:
                    for number, line in enumerate(handle, 1):
                        code = line.split("#")[0]
                        self.assertNotIn("sort" + "ed(", code, name + " line " + str(number))
                        self.assertNotIn("." + "sort(", code, name + " line " + str(number))


if __name__ == "__main__":
    unittest.main()
