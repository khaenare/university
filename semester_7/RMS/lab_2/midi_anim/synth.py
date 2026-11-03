"""Простий синтезатор: перетворює ноти на звук (numpy), щоб будь-який MIDI-файл звучав.

Мелодична нота — сума кількох гармонік (частоти f, 2f, 3f…) з обвідною
гучності: швидка атака → затухання → відпускання після note_off.
Ударні: бочка — синус зі спадною частотою, решта — короткий шум.
Кожна доріжка рендериться в окремий масив («стем»), тому доріжку можна
вимкнути миттєво — достатньо не додавати її стем до міксу.
"""
from __future__ import annotations

import functools

import numpy as np

from .midi_parser import Note, Song, drum_kind

SR = 44100        # частота дискретизації, Гц
RELEASE = 0.2     # відпускання після note_off, с
TAIL = 1.0        # тиша в кінці, щоб останні ноти встигли затухнути, с

# тембр за роллю доріжки: (амплітуди гармонік f, 2f, 3f…, швидкість затухання 1/с)
TIMBRES = {
    "melody": ([1.0, 0.3, 0.1], 4.0),
    "harmony": ([1.0, 0.5, 0.25, 0.12], 3.0),
    "bass": ([1.0, 0.45, 0.15], 1.5),
}


def midi_to_freq(pitch: int) -> float:
    """A4 (нота 69) = 440 Гц, кожен півтон — множник 2^(1/12)."""
    return 440.0 * 2 ** ((pitch - 69) / 12)


def tone(note: Note, role: str) -> np.ndarray:
    harmonics, decay = TIMBRES[role]
    freq = midi_to_freq(note.pitch)
    t = np.arange(int((note.duration + RELEASE) * SR)) / SR
    wave = sum(a * np.sin(2 * np.pi * freq * (k + 1) * t) for k, a in enumerate(harmonics)
               if freq * (k + 1) < SR / 2) / sum(harmonics)    # вище частоти Найквіста — спотворення
    attack = np.minimum(1.0, t / 0.005)
    release = np.clip((note.duration + RELEASE - t) / RELEASE, 0, 1)    # 1 до note_off, потім → 0
    return wave * attack * np.exp(-decay * t) * release


@functools.cache
def drum(pitch: int) -> np.ndarray:
    """Звук удару залежить лише від номера ноти, тому кожен рахуємо один раз (кеш)."""
    kind = drum_kind(pitch)
    rng = np.random.default_rng(pitch)
    if kind == "kick":                                      # бочка: частота падає 140 → 50 Гц
        t = np.arange(int(0.35 * SR)) / SR
        freq = 50 + 90 * np.exp(-t * 30)
        return np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 9)
    if kind == "snare":                                     # малий барабан, side stick, плеск — шум
        t = np.arange(int(0.2 * SR)) / SR
        return 0.6 * rng.uniform(-1, 1, len(t)) * np.exp(-t * 25)
    t = np.arange(int(0.12 * SR)) / SR                      # хай-хет, маракаси та інші — «сухий» шум
    return 0.4 * np.diff(rng.uniform(-1, 1, len(t) + 1)) * np.exp(-t * 40)


def render_stems(song: Song) -> list[np.ndarray]:
    """Для кожної доріжки — моно-масив float32 на всю тривалість пісні."""
    total = int((song.duration + TAIL) * SR)
    stems = []
    for track in song.tracks:
        stem = np.zeros(total, dtype=np.float32)
        for note in track.notes:
            wave = drum(note.pitch) if track.is_drums else tone(note, track.role)
            start = int(note.start * SR)
            end = min(total, start + len(wave))
            stem[start:end] += wave[: end - start] * (note.velocity / 127) * 0.5   # velocity → гучність
        stems.append(stem)
    return stems


def master_gain(stems: list[np.ndarray]) -> float:
    """Підсилення, з яким повний мікс має пік 0,9. Рахуємо один раз на пісню —
    тоді вимкнення доріжки не змінює гучність решти."""
    return 0.9 / (float(np.max(np.abs(sum(stems)))) or 1.0)


def mix(stems: list[np.ndarray], enabled: list[bool], gain: float) -> np.ndarray:
    """Сумує ввімкнені доріжки → 16-бітний стерео-масив для відтворення."""
    out = sum((s for s, on in zip(stems, enabled) if on), np.zeros_like(stems[0]))
    out = (np.clip(out * gain, -1, 1) * 32767).astype(np.int16)
    return np.column_stack([out, out])
