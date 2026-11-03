"""Анімація за MIDI: кожна нота стає об'єктом на екрані.

Відповідність MIDI → анімація:
  висота ноти        → координата X (низькі ноти ліворуч, високі праворуч)
  роль доріжки       → тип об'єкта: мелодія — зірки (вгорі), гармонія — бульбашки
                       (посередині), бас — хвиля (внизу), ударні — спалах фону,
                       кільце, іскри
  velocity           → розмір і яскравість; у бульбашок — швидкість підйому,
                       у хвилі — амплітуда
  note_on / note_off → поява / згасання об'єкта
  тривалість ноти    → скільки живе об'єкт

Кадр — це функція від часу t: стан кожного об'єкта обчислюється з початку
й кінця його ноти. Тому перемотування працює без накопичення помилок.
"""
from __future__ import annotations

import bisect
import math

import pygame

from .midi_parser import Note, Song, drum_kind, note_name

W, H = 1280, 720
COLORS = [(255, 196, 87), (90, 200, 250), (255, 110, 150), (140, 230, 140),
          (190, 140, 255), (255, 150, 80), (100, 240, 220), (240, 240, 120)]
DRUM_COLOR = (225, 230, 255)

MELODY_Y, HARMONY_Y, WAVE_Y = 270, 450, 590
FADE = 0.6          # скільки об'єкт згасає після note_off, с

OBJECTS = {"melody": "зірки", "harmony": "бульбашки", "bass": "хвиля", "drums": "спалах / кільце / іскри"}
DRUM_NAMES = {35: "Бочка", 36: "Бочка", 37: "Side stick", 38: "Малий барабан", 40: "Малий барабан",
              42: "Хай-хет", 46: "Відкритий хай-хет", 49: "Тарілка", 70: "Маракаси"}


def jitter(note: Note, k: int) -> float:
    """Сталий «випадковий» зсув 0…1: та сама нота завжди з'являється в тому самому місці."""
    return hash((note.track, note.pitch, round(note.start * 1000), k)) % 1000 / 1000


class Visualizer:
    def __init__(self, song: Song):
        self.song = song
        self.colors = [DRUM_COLOR if t.is_drums else COLORS[t.index % len(COLORS)] for t in song.tracks]
        pitches = [n.pitch for n in song.notes if not song.tracks[n.track].is_drums] or [48, 72]
        self.lo, self.hi = min(pitches) - 2, max(pitches) + 2
        bass = [n.pitch for n in song.notes if song.tracks[n.track].role == "bass"] or [36]
        self.bass_lo, self.bass_hi = min(bass), max(bass) + 1
        self.starts = [n.start for n in song.notes]
        self.track_starts = [[n.start for n in t.notes] for t in song.tracks]
        self.longest = max(n.duration for n in song.notes)
        self.sounding: set[int] = set()       # доріжки, ноти яких звучать у поточному кадрі
        self.overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        self.background = pygame.Surface((W, H))
        for y in range(H):                                   # нічне небо → море: вертикальний градієнт
            k = y / H
            pygame.draw.line(self.background, (int(8 + 4 * k), int(12 + 34 * k), int(30 + 44 * k)), (0, y), (W, y))

    # ---------- відповідність параметрів ----------
    def x_of(self, pitch: int) -> float:
        return 90 + (pitch - self.lo) / (self.hi - self.lo) * (W - 180)

    @staticmethod
    def size_of(note: Note) -> float:
        return 8 + 22 * note.velocity / 127

    @staticmethod
    def speed_of(note: Note) -> float:
        return 25 + 50 * note.velocity / 127               # px/с — гучніші бульбашки спливають швидше

    def wave_of(self, note: Note) -> tuple[float, float]:
        """Амплітуда хвилі (від velocity) і кількість хвиль на екран (вищий бас — дрібніші хвилі)."""
        return 10 + 40 * note.velocity / 127, 1.5 + 4 * (note.pitch - self.bass_lo) / (self.bass_hi - self.bass_lo)

    @staticmethod
    def level(t: float, note: Note) -> float:
        """Яскравість 0…1: швидка поява на note_on, згасання після note_off."""
        if t < note.end:
            return min(1.0, (t - note.start) / 0.05)
        return max(0.0, 1 - (t - note.end) / FADE)

    def describe(self, note: Note) -> str:
        """Рядок журналу: MIDI-подія → об'єкт і його параметри."""
        track = self.song.tracks[note.track]
        name = DRUM_NAMES.get(note.pitch, f"удар {note.pitch}") if track.is_drums else note_name(note.pitch)
        head = f"{track.name}: {name}, vel {note.velocity} →"
        if track.role == "melody":
            return f"{head} зірка x={self.x_of(note.pitch):.0f}, r={self.size_of(note):.0f}"
        if track.role == "harmony":
            return f"{head} бульбашка x={self.x_of(note.pitch):.0f}, {self.speed_of(note):.0f} px/с"
        if track.role == "bass":
            amplitude, waves = self.wave_of(note)
            return f"{head} хвиля: амплітуда {amplitude:.0f}, хвиль {waves:.1f}"
        return f"{head} " + {"kick": "спалах фону", "snare": "кільце", "hat": "іскри"}[drum_kind(note.pitch)]

    # ---------- малювання ----------
    def draw(self, surface: pygame.Surface, t: float, enabled: list[bool]):
        surface.blit(self.background, (0, 0))
        self.overlay.fill((0, 0, 0, 0))
        first = bisect.bisect_left(self.starts, t - self.longest - FADE)
        last = bisect.bisect_right(self.starts, t)
        visible = [n for n in self.song.notes[first:last] if enabled[n.track] and n.end + FADE > t]
        self.sounding = {n.track for n in visible if t < n.end}
        groups = {"melody": [], "harmony": [], "bass": [], "drums": []}
        for n in visible:
            groups[self.song.tracks[n.track].role].append(n)

        self.draw_drums(surface, t, groups["drums"])
        self.draw_wave(t, groups["bass"])
        for n in groups["harmony"]:
            self.draw_bubble(t, n)
        for n in groups["melody"]:
            self.draw_star(t, n)
        surface.blit(self.overlay, (0, 0))

    def glow(self, x, y, radius, color, level):
        """Світіння: концентричні кола, прозорість зростає до центру."""
        for i in range(4, 0, -1):
            pygame.draw.circle(self.overlay, (*color, int(level * 90 * (5 - i) / 4)), (x, y), radius * i / 4)

    def draw_star(self, t, n):
        level = self.level(t, n)
        if level <= 0:
            return
        x = self.x_of(n.pitch)
        y = MELODY_Y + (jitter(n, 1) - 0.5) * 80
        if t > n.end:
            y -= 60 * (1 - level)                           # згасаючи, зірка злітає вгору
        r = self.size_of(n)
        self.glow(x, y, r * 2.5, self.colors[n.track], level)
        pygame.draw.circle(self.overlay, (255, 255, 255, int(255 * level)), (x, y), max(2.0, r * 0.3))

    def draw_bubble(self, t, n):
        level = self.level(t, n)
        if level <= 0:
            return
        x = self.x_of(n.pitch) + (jitter(n, 2) - 0.5) * 24
        y = HARMONY_Y + (jitter(n, 3) - 0.5) * 80 - min(t - n.start, 4) * self.speed_of(n)
        r = self.size_of(n) * 0.8
        color = self.colors[n.track]
        pygame.draw.circle(self.overlay, (*color, int(90 * level)), (x, y), r)
        pygame.draw.circle(self.overlay, (*color, int(240 * level)), (x, y), r, 3)

    def draw_wave(self, t, bass):
        color = self.colors[bass[0].track] if bass else (60, 170, 200)
        points = []
        for x in range(0, W + 10, 10):
            y = WAVE_Y + 6 * math.sin(2 * math.pi * 1.2 * x / W + t)       # спокійна брижа
            for n in bass:
                amplitude, waves = self.wave_of(n)
                y -= amplitude * self.level(t, n) * math.sin(2 * math.pi * waves * x / W - t * 2.5)
            points.append((x, y))
        pygame.draw.polygon(self.overlay, (*[c // 3 for c in color], 160), points + [(W, H), (0, H)])
        pygame.draw.lines(self.overlay, (*color, 230), False, points, 3)

    def draw_drums(self, surface, t, drums):
        flash = 0.0
        for n in drums:
            age, strength = t - n.start, n.velocity / 127
            kind = drum_kind(n.pitch)
            if kind == "kick":                              # бочка → спалах усього фону
                flash += strength * math.exp(-age * 7)
            elif kind == "snare" and age < 0.4:             # малий барабан → кільце, що розходиться
                alpha = int(200 * (1 - age / 0.4) * strength)
                pygame.draw.circle(self.overlay, (*DRUM_COLOR, alpha), (W // 2, 330), 30 + age * 450, 3)
            elif kind == "hat" and age < 0.25:              # хай-хет, маракаси → іскри вгорі
                for i in range(3):
                    x = 120 + jitter(n, 10 + i) * (W - 240)
                    y = 90 + jitter(n, 20 + i) * 200
                    self.glow(x, y, 12 + 10 * strength, DRUM_COLOR, 1 - age / 0.25)
        if flash > 0.02:
            k = min(1.0, flash)
            surface.fill((int(35 * k), int(45 * k), int(80 * k)), special_flags=pygame.BLEND_ADD)
