"""Balance checker: plays many full seasons with a simple bot and prints win rates.

Usage:  python tools/simulate.py [games]
The bot is a "reasonable player": it expands, discovers crops, waters, harvests and sells.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import algorithms  # noqa: E402
import data  # noqa: E402
from game import FarmGame  # noqa: E402


def profit_per_day(game, crop):
    info = data.CROPS[crop]
    return (info["price"] - info["seed"]) / game.grow_days(crop)


def play(seed, skill):
    """skill: 'casual' (no upgrades, little care) / 'good' (expands) / 'idle' (does nothing)"""
    game = FarmGame(seed=seed)
    while not game.over:
        if skill == "idle":
            game.end_day()
            continue
        game.harvest_all()
        game.sell_all()
        if skill == "good":
            if game.day >= 2 and game.undiscovered() and game.coins >= 80:
                game.buy_packet()
            if 1 not in game.owned_fields and game.coins >= 260:
                game.buy_field(1)
            if "Bodega" not in game.upgrades and game.coins >= 150 and game.day > 4:
                game.buy_upgrade("Bodega")
            if 2 not in game.owned_fields and 1 in game.owned_fields and game.coins >= 520:
                game.buy_field(2)
            if "Irrigation" not in game.upgrades and game.coins >= 400:
                game.buy_upgrade("Irrigation")
            if "Scarecrow" not in game.upgrades and game.coins >= 300:
                game.buy_upgrade("Scarecrow")
        # plant the best crop that finishes before the season ends
        days_left = data.TOTAL_DAYS - game.day
        choices = [c for c in game.discovered if game.grow_days(c) <= days_left]
        choices = algorithms.selection_sort(choices, key=lambda c: profit_per_day(game, c), reverse=True)
        for cell in game.all_cells():
            if game.plots[cell] is None and game.is_unlocked(cell):
                for crop in choices:
                    ok, _ = game.plant(cell, crop)
                    if ok:
                        break
        if skill == "good":
            game.water_all()
        elif game.day % 2 == 0:
            game.water_all()
        game.end_day()
    return game


def main():
    games = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    for skill in ("idle", "casual", "good"):
        wins, coins, days = 0, 0, 0
        for seed in range(games):
            game = play(seed, skill)
            wins += 1 if game.won else 0
            coins += game.coins
            days += game.day
        print(f"{skill:7s} win rate {100 * wins / games:5.1f}%   avg coins {coins / games:8.0f}   avg last day {days / games:4.1f}")


if __name__ == "__main__":
    main()
