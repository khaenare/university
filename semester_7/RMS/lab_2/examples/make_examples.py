"""Створює набір вхідних файлів для демонстрації: коректні MIDI різних типів і некоректні файли.

Запуск із папки lab2:  python examples/make_examples.py
"""
from pathlib import Path

import mido

HERE = Path(__file__).resolve().parent
TPB = 480                       # тіків на чверть


def notes(channel, program, items):
    """items: (початок у долях, тривалість у долях, нота, velocity) → події (тік, повідомлення)."""
    events = [] if channel == 9 else [(0, mido.Message("program_change", channel=channel, program=program))]
    for beat, length, pitch, velocity in items:
        events.append((int(beat * TPB), mido.Message("note_on", channel=channel, note=pitch, velocity=velocity)))
        events.append((int((beat + length) * TPB), mido.Message("note_off", channel=channel, note=pitch, velocity=0)))
    return events


def track(name, events):
    """Абсолютні тіки → delta-time; у той самий момент note_off іде раніше за note_on."""
    result = mido.MidiTrack([mido.MetaMessage("track_name", name=name, time=0)])
    now = 0
    for tick, msg in sorted(events, key=lambda e: (e[0], e[1].type == "note_on")):
        result.append(msg.copy(time=tick - now))
        now = tick
    return result


def meta(bpm_changes, meter=(4, 4)):
    """Службова доріжка: розмір такту і темп; bpm_changes — [(доля, BPM)]."""
    events = [(0, mido.MetaMessage("time_signature", numerator=meter[0], denominator=meter[1]))]
    events += [(int(beat * TPB), mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm))) for beat, bpm in bpm_changes]
    return track("Tempo", events)


def save(name, tracks, midi_type=1):
    midi = mido.MidiFile(type=midi_type, ticks_per_beat=TPB)
    midi.tracks.extend(tracks)
    midi.save(HERE / name)


def melody(sequence, start=0.0, velocity=80, crescendo=0):
    """[(нота, тривалість)] → items; crescendo — на скільки зростає velocity до кінця."""
    items, beat = [], start
    for i, (pitch, length) in enumerate(sequence):
        items.append((beat, length, pitch, velocity + crescendo * i // len(sequence)))
        beat += length
    return items


CHORDS = {"Am": [57, 60, 64], "F": [53, 57, 60], "C": [55, 60, 64], "G": [55, 59, 62]}
ROOTS = {"Am": 45, "F": 41, "C": 48, "G": 43}


def main():
    # 1. Формат 0: одна доріжка з двома каналами — «Ода до радості» (Бетховен) з крещендо
    ode = [(76, 1), (76, 1), (77, 1), (79, 1), (79, 1), (77, 1), (76, 1), (74, 1),
           (72, 1), (72, 1), (74, 1), (76, 1)]
    tune = melody(ode + [(76, 1.5), (74, 0.5), (74, 2)] + ode + [(74, 1.5), (72, 0.5), (72, 2)],
                  velocity=45, crescendo=75)
    bass = [(bar * 4, 4, root, 85) for bar, root in enumerate([48, 43, 48, 43, 48, 43, 48, 48])]
    events = [(0, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120)))]
    events += notes(0, 0, tune) + notes(1, 32, bass)
    save("01_ode_to_joy_format0.mid", [track("Ode to Joy", events)], midi_type=0)

    # 2. Зміна темпу: 70 → 150 BPM, кожні 2 такти швидше
    progression = ["Am", "F", "C", "G"] * 4
    pad = [(bar * 4, 4, p, 60) for bar, name in enumerate(progression) for p in CHORDS[name]]
    arpeggio = [(bar * 4 + k * 0.5, 0.5, CHORDS[name][k % 3] + 12, 75)
                for bar, name in enumerate(progression) for k in range(8)]
    bass = [(bar * 4, 4, ROOTS[name], 90) for bar, name in enumerate(progression)]
    save("02_tempo_change.mid", [meta([(bar * 4, 70 + bar * 5) for bar in range(0, 16, 2)]),
                                 track("Pad", notes(0, 89, pad)), track("Arpeggio", notes(1, 4, arpeggio)),
                                 track("Bass", notes(2, 33, bass))])

    # 3. Вальс у розмірі 3/4: бас на першу долю, акорди на другу й третю
    waltz = ["C", "G", "C", "F", "C", "G", "C", "C"] * 2
    bass = [(bar * 3, 1, ROOTS[name], 90) for bar, name in enumerate(waltz)]
    chords = [(bar * 3 + beat, 1, p, 55) for bar, name in enumerate(waltz) for beat in (1, 2) for p in CHORDS[name]]
    line = [(76, 2), (79, 1), (77, 2), (74, 1), (76, 1), (79, 1), (84, 1), (81, 3),
            (79, 2), (76, 1), (74, 2), (77, 1), (76, 3), (72, 3)]
    save("03_waltz_3-4.mid", [meta([(0, 150)], meter=(3, 4)), track("Melody", notes(0, 73, melody(line * 2, velocity=85))),
                              track("Chords", notes(1, 0, chords)), track("Bass", notes(2, 32, bass))])

    # 4. Лише бас і ударні — без мелодії та гармонії
    drums = []
    for bar in range(8):
        b = bar * 4
        drums += [(b, 0.25, 36, 110), (b + 2.5, 0.25, 36, 90), (b + 1, 0.25, 38, 100), (b + 3, 0.25, 38, 100)]
        drums += [(b + k * 0.5, 0.2, 42, 50 + 30 * (k % 2 == 0)) for k in range(8)]
    funk = [(bar * 4 + beat, 0.4, root + shift, 100) for bar, root in enumerate([40, 40, 43, 45] * 2)
            for beat, shift in [(0, 0), (0.75, 12), (1.5, 0), (2.5, 7), (3, 10)]]
    save("04_drums_and_bass.mid", [meta([(0, 110)]), track("Drums", notes(9, 0, drums)),
                                   track("Bass", notes(1, 33, funk))])

    # 5. Шість доріжок: мелодія, підголосок, пед, арпеджіо, бас, ударні
    progression = ["Am", "F", "C", "G"] * 2
    lead = melody([(76, 1), (79, 1), (81, 2), (79, 1), (77, 1), (76, 2), (72, 1), (74, 1), (76, 2),
                   (74, 2), (71, 2)] * 2, velocity=90)
    counter = melody([(64, 2), (65, 2), (64, 4), (60, 2), (62, 2), (59, 4)] * 2, velocity=65)
    pad = [(bar * 4, 4, p, 50) for bar, name in enumerate(progression) for p in CHORDS[name]]
    arpeggio = [(bar * 4 + k * 0.25, 0.25, CHORDS[name][k % 3] + 12, 45 + 10 * (k % 4 == 0))
                for bar, name in enumerate(progression) for k in range(16)]
    bass = [(bar * 4 + beat, 1, ROOTS[name], 95) for bar, name in enumerate(progression) for beat in (0, 2)]
    drums = [(bar * 4 + beat, 0.25, pitch, 95) for bar in range(8) for beat, pitch in [(0, 36), (1, 38), (2, 36), (3, 38)]]
    drums += [(bar * 4 + k * 0.5, 0.2, 42, 55) for bar in range(8) for k in range(8)]
    save("05_six_tracks.mid", [meta([(0, 100)]), track("Lead", notes(0, 80, lead)), track("Counter", notes(1, 73, counter)),
                               track("Pad", notes(2, 89, pad)), track("Arpeggio", notes(3, 11, arpeggio)),
                               track("Bass", notes(4, 33, bass)), track("Drums", notes(9, 0, drums))])

    # 6. Лише одна доріжка — програма працює, але показує попередження
    scale = [(60 + step, 0.5) for step in [0, 2, 4, 5, 7, 9, 11, 12, 11, 9, 7, 5, 4, 2, 0]]
    save("06_one_track.mid", [meta([(0, 100)]), track("Scale", notes(0, 0, melody(scale, velocity=80)))])

    # 7–10. Некоректні вхідні дані
    save("07_no_notes.mid", [meta([(0, 120)])])                                  # коректний MIDI без жодної ноти
    (HERE / "08_text_renamed.mid").write_text("Це текстовий файл, якому змінили розширення на .mid\n", encoding="utf-8")
    (HERE / "09_truncated.mid").write_bytes((HERE / "05_six_tracks.mid").read_bytes()[:200])   # обрізаний файл
    (HERE / "10_not_midi.txt").write_text("Звичайний текстовий файл\n", encoding="utf-8")
    print("Створено файли в", HERE)


if __name__ == "__main__":
    main()
