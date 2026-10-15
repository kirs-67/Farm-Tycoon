"""Tests for the game rules (no window needed)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import data  # noqa: E402
from game import FarmGame  # noqa: E402


def grow_fully(game, cell, water=True):
    """Helper: pass days until the crop at `cell` is ready."""
    while not game.is_ready(cell) and not game.over:
        if water:
            game.water(cell)
        game.end_day()


class StartTests(unittest.TestCase):
    def test_starting_state(self):
        game = FarmGame(seed=1, events=False)
        self.assertEqual(game.day, 1)
        self.assertEqual(game.coins, data.START_COINS)
        self.assertFalse(game.over)
        self.assertEqual(game.bodega, [])
        self.assertEqual(game.discovered, {"Kangkong", "Mais", "Kamatis"})
        self.assertEqual(game.owned_fields, {0})

    def test_plots_use_tuple_keys(self):
        game = FarmGame(seed=1, events=False)
        self.assertEqual(len(game.plots), 24)
        for key in game.plots:
            self.assertIsInstance(key, tuple)


class PlantWaterTests(unittest.TestCase):
    def setUp(self):
        self.game = FarmGame(seed=1, events=False)

    def test_plant_costs_seed_money(self):
        ok, _ = self.game.plant((0, 0), "Mais")
        self.assertTrue(ok)
        self.assertEqual(self.game.coins, data.START_COINS - data.CROPS["Mais"]["seed"])

    def test_cannot_plant_in_locked_field(self):
        ok, message = self.game.plant((0, 5), "Mais")
        self.assertFalse(ok)
        self.assertIn("field", message)

    def test_cannot_plant_undiscovered_crop(self):
        ok, _ = self.game.plant((0, 0), "Mangga")
        self.assertFalse(ok)

    def test_cannot_plant_twice_on_same_plot(self):
        self.game.plant((0, 0), "Mais")
        ok, _ = self.game.plant((0, 0), "Kamatis")
        self.assertFalse(ok)

    def test_cannot_plant_without_money(self):
        self.game.coins = 1
        ok, _ = self.game.plant((0, 0), "Mais")
        self.assertFalse(ok)

    def test_water_once_per_day(self):
        self.game.plant((0, 0), "Mais")
        self.assertTrue(self.game.water((0, 0))[0])
        self.assertFalse(self.game.water((0, 0))[0])
        self.game.end_day()
        self.assertTrue(self.game.water((0, 0))[0])

    def test_water_empty_plot_fails(self):
        self.assertFalse(self.game.water((0, 0))[0])

    def test_water_all(self):
        self.game.plant((0, 0), "Mais")
        self.game.plant((0, 1), "Mais")
        ok, message = self.game.water_all()
        self.assertTrue(ok)
        self.assertIn("2", message)

    def test_crop_grows_after_days(self):
        self.game.plant((0, 0), "Kangkong")    # 2 days
        self.assertFalse(self.game.is_ready((0, 0)))
        self.game.end_day()
        self.game.end_day()
        self.assertTrue(self.game.is_ready((0, 0)))

    def test_rush_adds_a_day(self):
        self.game.plant((0, 0), "Mais")
        before = self.game.remaining((0, 0))
        self.assertTrue(self.game.rush((0, 0))[0])
        self.assertEqual(self.game.remaining((0, 0)), before - 1)


class SmartActionTests(unittest.TestCase):
    def setUp(self):
        self.game = FarmGame(seed=2, events=False)

    def test_empty_plot_plants(self):
        ok, _, kind = self.game.smart_action((0, 0), "Mais")
        self.assertTrue(ok)
        self.assertEqual(kind, "plant")
        self.assertIsNotNone(self.game.plots[(0, 0)])

    def test_thirsty_crop_gets_watered_once(self):
        self.game.smart_action((0, 0), "Mais")
        ok, _, kind = self.game.smart_action((0, 0), "Mais")
        self.assertEqual((ok, kind), (True, "water"))
        ok, _, kind = self.game.smart_action((0, 0), "Mais")
        self.assertEqual((ok, kind), (False, "info"))

    def test_ready_crop_gets_harvested(self):
        self.game.smart_action((0, 0), "Kangkong")
        for _ in range(2):
            self.game.end_day()
        ok, _, kind = self.game.smart_action((0, 0), "Kangkong")
        self.assertEqual((ok, kind), (True, "harvest"))
        self.assertEqual(len(self.game.bodega), 1)

    def test_locked_field_is_refused(self):
        ok, _, kind = self.game.smart_action((0, 5), "Mais")
        self.assertEqual((ok, kind), (False, "info"))


class HarvestTests(unittest.TestCase):
    def setUp(self):
        self.game = FarmGame(seed=7, events=False)

    def test_cannot_harvest_before_ready(self):
        self.game.plant((0, 0), "Mais")
        self.assertFalse(self.game.harvest((0, 0))[0])

    def test_harvest_moves_crop_to_bodega(self):
        self.game.plant((0, 0), "Kangkong")
        grow_fully(self.game, (0, 0))
        ok, _ = self.game.harvest((0, 0))
        self.assertTrue(ok)
        self.assertEqual(len(self.game.bodega), 1)
        self.assertIsNone(self.game.plots[(0, 0)])
        self.assertIn("First Harvest", self.game.achievements)

    def test_bodega_is_kept_in_order_by_insertion_sort(self):
        for cell, crop in [((0, 0), "Kangkong"), ((0, 1), "Kamatis"), ((1, 0), "Mais")]:
            self.game.plant(cell, crop)
        for _ in range(5):
            self.game.water_all()
            self.game.end_day()
        self.game.harvest_all()
        worths = [crate["worth"] for crate in self.game.bodega]
        self.assertEqual(len(worths), 3)
        for i in range(len(worths) - 1):
            self.assertGreaterEqual(worths[i], worths[i + 1])

    def test_harvest_discovers_crop(self):
        self.game.plant((0, 0), "Mais")
        grow_fully(self.game, (0, 0))
        self.game.harvest((0, 0))
        self.assertIn("Mais", self.game.discovered)

    def test_full_bodega_blocks_harvest(self):
        self.game.plant((0, 0), "Kangkong")
        self.game.bodega = [{"crop": "Mais", "quality": "Normal", "worth": 28}] * self.game.capacity()
        grow_fully(self.game, (0, 0))
        ok, message = self.game.harvest((0, 0))
        self.assertFalse(ok)
        self.assertIn("full", message)
        self.assertIsNotNone(self.game.plots[(0, 0)])

    def test_harvest_zone_uses_recursion_across_beds(self):
        for cell in [(0, 0), (1, 1), (2, 0), (3, 1)]:    # upper and lower beds
            self.game.plant(cell, "Kangkong")
        for _ in range(3):
            self.game.end_day()
        field = self.game.tree["children"][0]
        ok, message = self.game.harvest_zone(field)
        self.assertTrue(ok)
        self.assertEqual(len(self.game.bodega), 4)
        self.assertEqual(self.game.ready_count(), 0)

    def test_harvest_zone_with_nothing_ready(self):
        ok, _ = self.game.harvest_all()
        self.assertFalse(ok)

    def test_ready_value_adds_prices_recursively(self):
        self.game.plant((0, 0), "Kangkong")
        self.game.plant((3, 1), "Kangkong")
        for _ in range(3):
            self.game.end_day()
        expected = 2 * self.game.price_of("Kangkong")
        self.assertEqual(self.game.ready_value(), expected)

    def test_water_improves_quality_odds(self):
        watered, dry = 0, 0
        for seed in range(60):
            game = FarmGame(seed=seed)
            plot = {"crop": "Mais", "age": 3, "grow": 3, "watered_days": 3, "watered_today": False}
            if game.roll_quality(plot) != "Normal":
                watered += 1
            plot_dry = {"crop": "Mais", "age": 3, "grow": 3, "watered_days": 0, "watered_today": False}
            if game.roll_quality(plot_dry) != "Normal":
                dry += 1
        self.assertGreater(watered, dry)


class SellingTests(unittest.TestCase):
    def setUp(self):
        self.game = FarmGame(seed=3, events=False)
        self.game.bodega = [
            {"crop": "Mangga", "quality": "Normal", "worth": 270},
            {"crop": "Mais", "quality": "Premium", "worth": 45},
            {"crop": "Kangkong", "quality": "Normal", "worth": 12},
        ]
        self.game.discovered.add("Mangga")

    def test_sell_crate_adds_coins_and_lowers_price(self):
        before = self.game.coins
        ok, _ = self.game.sell_crate(1)
        self.assertTrue(ok)
        self.assertGreater(self.game.coins, before)
        self.assertLess(self.game.index["Mais"], 1.0)
        self.assertEqual(len(self.game.bodega), 2)

    def test_sell_bad_position(self):
        self.assertFalse(self.game.sell_crate(9)[0])
        self.assertFalse(self.game.sell_crate(-1)[0])

    def test_sell_best_picks_highest_price(self):
        before = self.game.coins
        self.game.sell_best()
        self.assertEqual(self.game.coins - before, 270)

    def test_sell_best_empty(self):
        self.game.bodega = []
        self.assertFalse(self.game.sell_best()[0])

    def test_sell_all_empties_bodega_and_big_sale(self):
        self.game.bodega += [{"crop": "Mangga", "quality": "Normal", "worth": 270}] * 3
        ok, _ = self.game.sell_all()
        self.assertTrue(ok)
        self.assertEqual(self.game.bodega, [])
        self.assertIn("Big Sale", self.game.achievements)

    def test_fiesta_pays_more(self):
        normal = self.game.price_of("Mais")
        self.game.day = 10
        self.assertGreater(self.game.price_of("Mais"), normal)

    def test_selling_everything_to_goal_wins(self):
        self.game.coins = self.game.goal - 5
        self.game.sell_crate(0)
        self.assertTrue(self.game.over)
        self.assertTrue(self.game.won)


class RankingAndFindingTests(unittest.TestCase):
    def setUp(self):
        self.game = FarmGame(seed=3, events=False)

    def test_market_ranking_is_sorted_high_to_low(self):
        self.game.discovered.update(["Mangga", "Palay"])
        ranking = self.game.market_ranking()
        prices = [price for _, price in ranking]
        for i in range(len(prices) - 1):
            self.assertGreaterEqual(prices[i], prices[i + 1])
        self.assertEqual(ranking[0][0], "Mangga")
        self.assertEqual(len(ranking), 5)

    def test_market_ranking_only_shows_discovered(self):
        names = [name for name, _ in self.game.market_ranking()]
        self.assertNotIn("Mangga", names)

    def test_market_ranking_fills_lab_log(self):
        self.game.market_ranking()
        self.assertGreater(len(self.game.lab["bubble"]), 1)

    def test_soonest_plot_none_when_nothing_growing(self):
        self.assertIsNone(self.game.soonest_plot())

    def test_soonest_plot_finds_least_time_left(self):
        self.game.plant((0, 0), "Mais")        # 3 days
        self.game.plant((0, 1), "Kangkong")    # 2 days
        self.game.plant((1, 0), "Kamatis")     # 3 days
        cell, left = self.game.soonest_plot()
        self.assertEqual(cell, (0, 1))
        self.assertEqual(left, 2)

    def test_soonest_plot_ignores_ready_crops(self):
        self.game.plant((0, 0), "Kangkong")
        self.game.end_day()
        self.game.end_day()
        self.game.plant((0, 1), "Mais")
        cell, _ = self.game.soonest_plot()
        self.assertEqual(cell, (0, 1))


class ShoppingTests(unittest.TestCase):
    def setUp(self):
        self.game = FarmGame(seed=3, events=False)
        self.game.coins = 2000

    def test_buy_field_unlocks_plots(self):
        self.assertTrue(self.game.buy_field(1)[0])
        self.assertTrue(self.game.plant((0, 2), "Mais")[0])

    def test_cannot_buy_field_twice(self):
        self.game.buy_field(1)
        self.assertFalse(self.game.buy_field(1)[0])

    def test_all_fields_gives_land_baron(self):
        self.game.buy_field(1)
        self.game.buy_field(2)
        self.assertIn("Land Baron", self.game.achievements)

    def test_not_enough_coins(self):
        self.game.coins = 10
        self.assertFalse(self.game.buy_field(1)[0])
        self.assertFalse(self.game.buy_upgrade("Irrigation")[0])
        self.assertFalse(self.game.buy_packet()[0])

    def test_bodega_upgrade_adds_capacity(self):
        before = self.game.capacity()
        self.game.buy_upgrade("Bodega")
        self.assertEqual(self.game.capacity(), before + data.BODEGA_BONUS)

    def test_irrigation_speeds_growth(self):
        self.game.buy_upgrade("Irrigation")
        self.game.plant((0, 0), "Mais")
        self.assertEqual(self.game.remaining((0, 0)), 2)

    def test_irrigation_never_below_two_days(self):
        self.game.buy_upgrade("Irrigation")
        self.assertEqual(self.game.grow_days("Kangkong"), 2)

    def test_upgrade_only_once(self):
        self.game.buy_upgrade("Scarecrow")
        self.assertFalse(self.game.buy_upgrade("Scarecrow")[0])

    def test_packet_discovers_new_crop_in_set(self):
        before = len(self.game.discovered)
        self.assertTrue(self.game.buy_packet()[0])
        self.assertEqual(len(self.game.discovered), before + 1)

    def test_packets_run_out_and_naturalist_unlocks(self):
        for _ in range(5):
            self.assertTrue(self.game.buy_packet()[0])
        self.assertFalse(self.game.buy_packet()[0])
        self.assertEqual(len(self.game.discovered), 8)
        self.assertIn("Naturalist", self.game.achievements)

    def test_set_has_no_duplicates(self):
        self.assertFalse(self.game.discover("Mais"))


class EventTests(unittest.TestCase):
    def setUp(self):
        self.game = FarmGame(seed=5, events=False)
        for cell in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            self.game.plant(cell, "Mais")

    def test_rain_waters_everything(self):
        self.game.run_event("rain")
        self.assertTrue(all(self.game.plots[c]["watered_today"] for c in self.game.planted_cells()))

    def test_typhoon_with_shield_is_harmless(self):
        self.game.upgrades.add("Storm Shield")
        self.game.run_event("typhoon")
        self.assertEqual(len(self.game.planted_cells()), 4)
        self.assertIn("Storm Survivor", self.game.achievements)

    def test_typhoon_without_shield_can_destroy(self):
        total_lost = 0
        for seed in range(30):
            game = FarmGame(seed=seed)
            for cell in [(0, 0), (0, 1), (1, 0), (1, 1)]:
                game.plant(cell, "Mais")
            game.run_event("typhoon")
            total_lost += 4 - len(game.planted_cells())
        self.assertGreater(total_lost, 0)

    def test_scarecrow_stops_pests(self):
        self.game.upgrades.add("Scarecrow")
        self.game.run_event("pests")
        self.assertEqual(len(self.game.planted_cells()), 4)

    def test_pests_destroy_some_crops(self):
        self.game.run_event("pests")
        self.assertEqual(len(self.game.planted_cells()), 2)

    def test_glut_and_demand_change_prices(self):
        game = FarmGame(seed=2)
        game.run_event("glut")
        self.assertTrue(any(v < 1.0 for v in game.index.values()))
        game = FarmGame(seed=2)
        game.run_event("demand")
        self.assertTrue(any(v > 1.0 for v in game.index.values()))

    def test_gift_adds_coins(self):
        before = self.game.coins
        self.game.run_event("gift")
        self.assertGreater(self.game.coins, before)

    def test_seedswap_discovers(self):
        before = len(self.game.discovered)
        self.game.run_event("seedswap")
        self.assertEqual(len(self.game.discovered), before + 1)

    def test_every_event_name_in_data_is_handled(self):
        for name in data.EVENTS:
            game = FarmGame(seed=9)
            game.plant((0, 0), "Mais")
            game.run_event(name)
            self.assertIsNotNone(game.today_event)
            self.assertEqual(game.today_event[0], name)

    def test_pick_event_returns_known_names(self):
        for _ in range(100):
            self.assertIn(self.game.pick_event(), data.EVENTS)


class DayAndEndingTests(unittest.TestCase):
    def test_end_day_advances_calendar(self):
        game = FarmGame(seed=1, events=False)
        game.end_day()
        self.assertEqual(game.day, 2)

    def test_prices_stay_in_bounds(self):
        game = FarmGame(seed=11)
        for _ in range(29):
            game.end_day()
            for value in game.index.values():
                self.assertGreaterEqual(value, data.MIN_INDEX)
                self.assertLessEqual(value, data.MAX_INDEX)

    def test_season_ends_after_last_day_with_loss(self):
        game = FarmGame(seed=1, events=False)
        for _ in range(data.TOTAL_DAYS):
            game.end_day()
        self.assertTrue(game.over)
        self.assertFalse(game.won)
        self.assertEqual(game.day, data.TOTAL_DAYS)

    def test_season_ends_with_win_if_rich(self):
        game = FarmGame(seed=1, events=False)
        game.coins = game.goal
        game.day = data.TOTAL_DAYS
        game.end_day()
        self.assertTrue(game.over)
        self.assertTrue(game.won)

    def test_actions_blocked_after_game_over(self):
        game = FarmGame(seed=1, events=False)
        game.over = True
        self.assertFalse(game.plant((0, 0), "Mais")[0])
        self.assertFalse(game.end_day()[0])
        self.assertFalse(game.buy_packet()[0])
        self.assertFalse(game.sell_all()[0])

    def test_restart_resets_everything(self):
        game = FarmGame(seed=1, events=False)
        game.plant((0, 0), "Mais")
        game.coins = 5
        game.end_day()
        game.new_game()
        self.assertEqual(game.day, 1)
        self.assertEqual(game.coins, data.START_COINS)
        self.assertIsNone(game.plots[(0, 0)])
        self.assertFalse(game.over)
        self.assertEqual(game.achievements, set())

    def test_fiesta_banner_on_fiesta_day(self):
        game = FarmGame(seed=1, events=False)
        game.day = 9
        game.end_day()
        self.assertEqual(game.day, 10)
        self.assertEqual(game.today_event[0], "fiesta")

    def test_rank_titles(self):
        game = FarmGame(seed=1, events=False)
        game.coins = 0
        self.assertIn("Rookie", game.rank())
        game.coins = 9000
        self.assertIn("Legend", game.rank())

    def test_difficulty_changes_goal_and_restarts(self):
        game = FarmGame(seed=1, events=False)
        game.coins = 999
        game.set_difficulty("Hard")
        self.assertEqual(game.goal, data.DIFFICULTIES["Hard"])
        self.assertEqual(game.coins, data.START_COINS)
        game.set_difficulty("Easy")
        self.assertLess(game.goal, data.DIFFICULTIES["Hard"])

    def test_same_seed_same_game(self):
        a, b = FarmGame(seed=42), FarmGame(seed=42)
        for _ in range(10):
            a.end_day()
            b.end_day()
        self.assertEqual(a.index, b.index)
        self.assertEqual(a.coins, b.coins)


if __name__ == "__main__":
    unittest.main()
