"""Тести парсера MIDI: переведення часу, зведення нот, ролі доріжок."""
import tempfile
import unittest
from pathlib import Path

import mido

from midi_anim.midi_parser import DRUM_NOTE, TempoMap, load_song, note_name

ASSETS = Path(__file__).resolve().parent.parent / "assets"


class TempoMapTest(unittest.TestCase):
    def test_constant_tempo(self):
        tempo = TempoMap([(0, 600_000)], ticks_per_beat=480)       # 100 BPM: чверть = 0,6 с
        self.assertAlmostEqual(tempo.to_seconds(480), 0.6)
        self.assertAlmostEqual(tempo.to_seconds(1920), 2.4)

    def test_tempo_change(self):
        tempo = TempoMap([(0, 600_000), (960, 300_000)], ticks_per_beat=480)
        self.assertAlmostEqual(tempo.to_seconds(960), 1.2)         # дві чверті по 0,6 с
        self.assertAlmostEqual(tempo.to_seconds(1440), 1.5)        # далі чверть = 0,3 с

    def test_default_tempo(self):
        tempo = TempoMap([], ticks_per_beat=480)                   # без set_tempo — 120 BPM
        self.assertAlmostEqual(tempo.to_seconds(480), 0.5)


class LoadSongTest(unittest.TestCase):
    def setUp(self):
        self.folder = Path(self.enterContext(tempfile.TemporaryDirectory()))   # видаляється після тесту

    def make_midi(self, tracks, ticks_per_beat=480) -> Path:
        """tracks — списки повідомлень mido з delta-time."""
        midi = mido.MidiFile(type=1, ticks_per_beat=ticks_per_beat)
        for messages in tracks:
            midi.tracks.append(mido.MidiTrack(messages))
        path = self.folder / "test.mid"
        midi.save(path)
        return path

    def test_note_pairing(self):
        path = self.make_midi([
            [mido.MetaMessage("set_tempo", tempo=500_000, time=0)],
            [mido.Message("program_change", program=0, time=0),
             mido.Message("note_on", note=60, velocity=100, time=0),
             mido.Message("note_on", note=60, velocity=0, time=480),     # velocity 0 = note_off
             mido.Message("note_on", note=64, velocity=70, time=0),
             mido.Message("note_off", note=64, velocity=0, time=240),
             mido.Message("note_on", note=67, velocity=50, time=0)],     # без note_off
            [mido.Message("note_on", note=36, velocity=90, channel=9, time=0),
             mido.Message("note_off", note=36, velocity=0, channel=9, time=120)],
        ])
        song = load_song(path)
        self.assertEqual(len(song.tracks), 2)                      # доріжка темпу без нот відкидається
        notes = song.tracks[0].notes
        self.assertEqual([(n.pitch, n.velocity) for n in notes], [(60, 100), (64, 70), (67, 50)])
        self.assertAlmostEqual(notes[0].start, 0.0)
        self.assertAlmostEqual(notes[0].end, 0.5)
        self.assertAlmostEqual(notes[1].end, 0.75)
        self.assertGreater(notes[2].duration, 0)                   # незакрита нота отримала тривалість
        self.assertEqual(song.tracks[1].role, "drums")
        self.assertEqual(song.warnings, [])

    def test_unclosed_drum_note_is_short(self):
        path = self.make_midi([
            [mido.Message("note_on", note=60, velocity=80, time=0),
             mido.Message("note_off", note=60, velocity=0, time=4800)],
            [mido.Message("note_on", note=42, velocity=80, channel=9, time=0),   # удар без note_off
             mido.Message("note_on", note=36, velocity=80, channel=9, time=4800)],
        ])
        drums = load_song(path).tracks[1]
        self.assertTrue(all(n.duration <= DRUM_NOTE for n in drums.notes))

    def test_tempo_changes(self):
        path = self.make_midi([
            [mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0),
             mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=480)],   # через 1 с — 120 BPM
            [mido.Message("note_on", note=60, velocity=80, time=0),
             mido.Message("note_off", note=60, velocity=0, time=960)],
            [mido.Message("note_on", note=72, velocity=80, time=0),
             mido.Message("note_off", note=72, velocity=0, time=960)],
        ])
        song = load_song(path)
        self.assertAlmostEqual(song.bpm_at(0.5), 60)
        self.assertAlmostEqual(song.bpm_at(1.2), 120)
        self.assertAlmostEqual(song.duration, 1.5)        # 1 с при 60 BPM + 0,5 с при 120 BPM

    def test_meter(self):
        path = self.make_midi([
            [mido.MetaMessage("time_signature", numerator=6, denominator=8, time=0),
             mido.Message("note_on", note=60, velocity=80, time=0),
             mido.Message("note_off", note=60, velocity=0, time=480)],
            [mido.Message("note_on", note=72, velocity=80, time=0),
             mido.Message("note_off", note=72, velocity=0, time=480)],
        ])
        self.assertEqual(load_song(path).meter, (6, 8))

    def test_format0_split_by_channel(self):
        path = self.make_midi([[
            mido.Message("note_on", note=72, velocity=80, channel=0, time=0),
            mido.Message("note_on", note=38, velocity=80, channel=9, time=0),
            mido.Message("note_off", note=72, velocity=0, channel=0, time=480),
            mido.Message("note_off", note=38, velocity=0, channel=9, time=0),
        ]])
        song = load_song(path)
        self.assertEqual(len(song.tracks), 2)
        self.assertEqual({t.role for t in song.tracks}, {"melody", "drums"})

    def test_invalid_files(self):
        text = self.folder / "text.mid"
        text.write_text("це не MIDI", encoding="utf-8")
        empty = self.folder / "empty.mid"
        empty.write_bytes(b"")
        truncated = self.folder / "truncated.mid"
        truncated.write_bytes((ASSETS / "atlantic_breeze.mid").read_bytes()[:300])
        cases = [(text, "не є MIDI"), (empty, "не є MIDI"), (truncated, "не є MIDI"),
                 (self.folder / "missing.mid", "не знайдено")]
        for path, message in cases:
            with self.subTest(file=path.name), self.assertRaisesRegex(ValueError, message):
                load_song(path)

    def test_no_notes(self):
        path = self.make_midi([[mido.MetaMessage("set_tempo", tempo=500_000, time=0)]])
        with self.assertRaisesRegex(ValueError, "немає жодної ноти"):
            load_song(path)

    def test_single_track_warning(self):
        path = self.make_midi([[mido.Message("note_on", note=60, velocity=80, time=0),
                                mido.Message("note_off", note=60, velocity=0, time=480)]])
        self.assertEqual(len(load_song(path).warnings), 1)

    def test_demo_song(self):
        song = load_song(ASSETS / "atlantic_breeze.mid")
        self.assertAlmostEqual(song.bpm_at(0), 100)
        self.assertEqual(song.meter, (4, 4))
        roles = {t.name: t.role for t in song.tracks}
        self.assertEqual(roles, {"Guitar": "harmony", "Bass": "bass", "Melody": "melody", "Percussion": "drums"})
        self.assertAlmostEqual(song.duration, 67.3, delta=0.5)


class NoteNameTest(unittest.TestCase):
    def test_names(self):
        self.assertEqual(note_name(60), "C4")
        self.assertEqual(note_name(69), "A4")
        self.assertEqual(note_name(37), "C#2")


if __name__ == "__main__":
    unittest.main()
