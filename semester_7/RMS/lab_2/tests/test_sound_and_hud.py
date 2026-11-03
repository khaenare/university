"""Тести синтезатора і форматування часу в інтерфейсі."""
import unittest

import numpy as np

from midi_anim.hud import clock
from midi_anim.midi_parser import Note
from midi_anim.synth import SR, mix, tone


class ClockTest(unittest.TestCase):
    def test_format(self):
        self.assertEqual(clock(0), "0:00.0")
        self.assertEqual(clock(68.3), "1:08.3")
        self.assertEqual(clock(59.97), "1:00.0")      # округлення переходить у хвилини


class SynthTest(unittest.TestCase):
    def test_no_harmonics_above_nyquist(self):
        """Найвища нота: гармоніки вище SR/2 відкинуті, тому в спектрі немає «віддзеркалених» частот."""
        note = Note(track=0, channel=0, pitch=127, velocity=100, start=0.0, end=0.5)
        wave = tone(note, "harmony")
        spectrum = np.abs(np.fft.rfft(wave))
        freqs = np.fft.rfftfreq(len(wave), 1 / SR)
        peak = freqs[np.argmax(spectrum)]
        self.assertAlmostEqual(peak, 440 * 2 ** ((127 - 69) / 12), delta=5)
        self.assertLess(spectrum[freqs < 10_000].max(), spectrum.max() * 0.01)

    def test_mix_keeps_gain_when_track_muted(self):
        stems = [np.full(10, 0.5, dtype=np.float32), np.full(10, 0.25, dtype=np.float32)]
        both = mix(stems, [True, True], gain=1.0)
        first = mix(stems, [True, False], gain=1.0)
        self.assertEqual(both.shape, (10, 2))
        self.assertLess(first[0, 0], both[0, 0])     # вимкнення доріжки не «підтягує» гучність решти


if __name__ == "__main__":
    unittest.main()
