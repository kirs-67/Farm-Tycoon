"""Tests for the sound system (no speakers needed)."""

import os
import sys
import unittest
import wave

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sounds  # noqa: E402

GAME_SOUNDS = ("click", "plant", "water", "harvest", "sell", "buy", "boost", "error", "day", "rain",
               "thunder", "pests", "gift", "down", "discover", "achieve", "fiesta", "win", "lose")


class SynthesisTests(unittest.TestCase):
    def test_every_game_sound_exists(self):
        built = sounds.build_sounds()
        for name in GAME_SOUNDS:
            self.assertIn(name, built)
            self.assertGreater(len(built[name]), 100)

    def test_tone_length_and_range(self):
        samples = sounds.tone(440, 0.1, 0.5)
        self.assertEqual(len(samples), int(sounds.RATE * 0.1))
        self.assertTrue(all(-1.0 <= value <= 1.0 for value in samples))

    def test_wav_files_are_valid(self):
        played = []
        board = sounds.SoundBoard(player=played.append)
        self.assertTrue(board.available)
        for name in GAME_SOUNDS:
            with wave.open(board.files[name]) as handle:
                self.assertEqual(handle.getnchannels(), 1)
                self.assertGreater(handle.getnframes(), 100)


class PlayingTests(unittest.TestCase):
    def setUp(self):
        self.played = []
        self.board = sounds.SoundBoard(player=self.played.append)

    def test_play_sends_the_right_file(self):
        self.board.play("harvest")
        self.assertEqual(len(self.played), 1)
        self.assertTrue(self.played[0].endswith("harvest.wav"))

    def test_mute_stops_sound(self):
        self.board.toggle()
        self.board.play("harvest")
        self.assertEqual(self.played, [])
        self.board.toggle()
        self.board.play("harvest")
        self.assertEqual(len(self.played), 2)      # the unmute click + the harvest

    def test_unknown_sound_is_ignored(self):
        self.board.play("does-not-exist")
        self.assertEqual(self.played, [])

    def test_no_player_means_silent_but_safe(self):
        silent = sounds.SoundBoard(player=None)
        self.assertFalse(silent.available)
        silent.play("sell")
        silent.toggle()

    def test_broken_player_never_crashes(self):
        def broken(path):
            raise OSError("no speakers")
        board = sounds.SoundBoard(player=broken)
        board.play("sell")
        self.assertFalse(board.available)


if __name__ == "__main__":
    unittest.main()
