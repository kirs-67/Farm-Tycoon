"""Sound effects for Bukid Tycoon.

Tkinter cannot play audio, so this file does two things using only the standard library:
  1. SYNTHESISES every sound effect as a small .wav file (sine waves + noise + a fade-out),
     so the project needs no audio files and no extra packages.
  2. PLAYS them with whatever the computer offers:
         Windows -> winsound (built into Python)
         macOS   -> the `afplay` command
         Linux   -> `paplay`, `aplay` or `play` if one is installed
If nothing can play sound, the game simply stays silent. It never crashes because of audio.

Usage:   board = SoundBoard();  board.play("harvest");  board.toggle()   # mute / unmute
"""

import atexit
import math
import os
import random
import shutil
import struct
import subprocess
import sys
import tempfile
import wave

RATE = 22050


# ----------------------------------------------------------------------------
# Making the sounds (plain maths)
# ----------------------------------------------------------------------------
def tone(freq, seconds, volume=0.5, shape="sine", end_freq=None):
    """Return a list of samples (numbers from -1 to 1) for one note that fades out.

    end_freq makes the pitch slide from `freq` to `end_freq` (used for pops and buzzes).
    """
    count = int(RATE * seconds)
    samples = []
    phase = 0.0
    for i in range(count):
        progress = i / max(1, count - 1)
        current = freq if end_freq is None else freq + (end_freq - freq) * progress
        phase += 2 * math.pi * current / RATE
        if shape == "square":
            value = 1.0 if math.sin(phase) >= 0 else -1.0
        elif shape == "triangle":
            value = 2 / math.pi * math.asin(math.sin(phase))
        else:
            value = math.sin(phase)
        fade_in = min(1.0, i / 60)                 # tiny fade-in so notes do not click
        fade_out = (1.0 - progress) ** 1.6         # smooth fade-out
        samples.append(value * volume * fade_in * fade_out)
    return samples


def noise(seconds, volume=0.3, smooth=0.0, seed=1):
    """Random hiss (rain). `smooth` close to 1 makes it a deeper rumble (thunder)."""
    rng = random.Random(seed)
    count = int(RATE * seconds)
    samples = []
    last = 0.0
    for i in range(count):
        progress = i / max(1, count - 1)
        raw = rng.uniform(-1, 1)
        last = last * smooth + raw * (1 - smooth)
        envelope = min(1.0, i / 800) * (1.0 - progress) ** 0.8
        samples.append(last * volume * envelope)
    return samples


def mix(*parts):
    """Play several sample lists at the same time."""
    length = max(len(part) for part in parts)
    out = [0.0] * length
    for part in parts:
        for i, value in enumerate(part):
            out[i] += value
    return out


def join(*parts):
    """Play sample lists one after another."""
    out = []
    for part in parts:
        out += part
    return out


def silence(seconds):
    return [0.0] * int(RATE * seconds)


def melody(notes, length=0.1, volume=0.45, shape="sine", gap=0.0):
    """A list of frequencies played one after another."""
    parts = []
    for freq in notes:
        parts.append(tone(freq, length, volume, shape))
        if gap:
            parts.append(silence(gap))
    return join(*parts)


# Note names make the melodies easier to read (frequencies in Hz).
C4, D4, E4, G4, A4, B4 = 261.6, 293.7, 329.6, 392.0, 440.0, 493.9
C5, D5, E5, F5, G5, A5, B5 = 523.3, 587.3, 659.3, 698.5, 784.0, 880.0, 987.8
C6, E6, G6 = 1046.5, 1318.5, 1568.0


def build_sounds():
    """Return {sound name: samples}. Every name here can be played with SoundBoard.play()."""
    return {
        "click": tone(880, 0.04, 0.3, "triangle"),
        "plant": join(tone(330, 0.09, 0.5, "sine", end_freq=140), tone(660, 0.05, 0.25)),
        "water": melody([620, 760, 900], 0.05, 0.35),
        "harvest": mix(melody([A5, E6], 0.1, 0.4), melody([A5 / 2, E6 / 2], 0.1, 0.2)),
        "sell": melody([E6, C6 * 2, G6 * 1.0], 0.07, 0.38, "triangle"),
        "buy": melody([C5, E5, G5, C6], 0.07, 0.4),
        "boost": join(tone(500, 0.08, 0.4, "triangle", end_freq=900), tone(1000, 0.1, 0.3)),
        "error": tone(170, 0.18, 0.35, "square", end_freq=120),
        "day": melody([G4, B4, D5], 0.13, 0.4, "triangle"),
        "rain": mix(noise(0.7, 0.28, 0.35, seed=4), melody([1200, 1500, 1100, 1700], 0.04, 0.08, gap=0.12)),
        "thunder": mix(noise(0.95, 0.7, 0.93, seed=7), tone(70, 0.9, 0.5, "sine", end_freq=45)),
        "pests": join(tone(420, 0.06, 0.3, "square"), tone(470, 0.06, 0.3, "square"),
                      tone(420, 0.06, 0.3, "square"), tone(470, 0.06, 0.3, "square")),
        "gift": melody([C5, E5, G5, C6, E6], 0.07, 0.4, "triangle"),
        "down": tone(500, 0.22, 0.35, "triangle", end_freq=260),
        "discover": melody([G5, B5, D5 * 2, G5 * 2], 0.09, 0.38),
        "achieve": melody([C5, E5, G5, C6], 0.12, 0.45, "triangle"),
        "fiesta": melody([C5, E5, G5, E5, G5, C6, E6, C6], 0.09, 0.4, "triangle"),
        "win": join(melody([C5, C5, C5, G5], 0.13, 0.5, "triangle"),
                    mix(melody([A5, B5 * 1.0], 0.2, 0.45, "triangle"), melody([F5, G5], 0.2, 0.3)),
                    mix(tone(C6, 0.5, 0.45, "triangle"), tone(G5, 0.5, 0.3, "triangle"),
                        tone(E5, 0.5, 0.3, "triangle"))),
        "lose": melody([G4, F5 * 0.5 * 1.5, E4, C4], 0.26, 0.4, "triangle"),
    }


def write_wav(path, samples):
    """Save samples as a 16-bit mono .wav file."""
    frames = bytearray()
    for value in samples:
        value = max(-1.0, min(1.0, value))
        frames += struct.pack("<h", int(value * 32000))
    with wave.open(path, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(RATE)
        handle.writeframes(bytes(frames))


# ----------------------------------------------------------------------------
# Playing the sounds
# ----------------------------------------------------------------------------
def find_player():
    """Return a function play(path) for this computer, or None when sound is impossible."""
    if sys.platform.startswith("win"):
        try:
            import winsound

            def play_windows(path):
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)

            return play_windows
        except ImportError:
            return None

    if sys.platform == "darwin":
        command = ["afplay"]
    else:
        command = None
        for name in ("paplay", "aplay", "play"):
            if shutil.which(name):
                command = [name] + (["-q"] if name == "play" else [])
                break
    if command is None or shutil.which(command[0]) is None:
        return None

    def play_command(path):
        subprocess.Popen(command + [path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return play_command


class SoundBoard:
    """Builds the sound files once, then plays them by name."""

    def __init__(self, player="auto"):
        self.enabled = True
        self.files = {}
        self.folder = None
        self.player = find_player() if player == "auto" else player
        self.available = False
        if self.player is None:
            return
        try:
            self.folder = tempfile.mkdtemp(prefix="bukid_sounds_")
            atexit.register(shutil.rmtree, self.folder, True)
            for name, samples in build_sounds().items():
                path = os.path.join(self.folder, name + ".wav")
                write_wav(path, samples)
                self.files[name] = path
            self.available = True
        except Exception:        # any problem with audio must never stop the game
            self.available = False

    def play(self, name):
        if not (self.enabled and self.available):
            return
        path = self.files.get(name)
        if path is None:
            return
        try:
            self.player(path)
        except Exception:
            self.available = False

    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled:
            self.play("click")
        return self.enabled
