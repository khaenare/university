"""Інтерфейс поверх анімації: легенда доріжок, журнал подій, смуга прогресу."""
from __future__ import annotations

import bisect
from pathlib import Path

import pygame

from .midi_parser import Song
from .visuals import H, OBJECTS, W, Visualizer

FONT_FILES = [   # шрифти з кирилицею: macOS, Windows, Linux
    ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]
ROLE_NAMES = {"melody": "мелодія", "harmony": "гармонія", "bass": "бас", "drums": "ударні"}
TEXT, DIM, MUTED = (230, 235, 245), (130, 140, 165), (80, 85, 100)
BAR = pygame.Rect(40, H - 44, W - 320, 8)            # смуга прогресу — по ній можна клікнути
HINT = "Пробіл — пуск/пауза    ←/→ — ±5 с    1–9 — вимкнути доріжку    перетягніть .mid у вікно    Esc — вихід"
LOG_LINES = 5


def load_font(size: int, bold: bool = False) -> pygame.font.Font:
    for regular, heavy in FONT_FILES:
        path = heavy if bold else regular
        if Path(path).exists():
            return pygame.font.Font(path, size)
    return pygame.font.Font(None, size + 4)


def clock(seconds: float) -> str:
    """68.3 → '1:08.3'. Округлюємо до десятих до поділу на хвилини, щоб не було '0:60.0'."""
    tenths = round(seconds * 10)
    return f"{tenths // 600}:{tenths % 600 / 10:04.1f}"


class Hud:
    def __init__(self, song: Song, visual: Visualizer):
        self.song, self.visual = song, visual
        self.font, self.small = load_font(15), load_font(13)
        self.bold, self.title = load_font(15, bold=True), load_font(18, bold=True)
        self._shades: dict = {}

    def text(self, surface, text, pos, font=None, color=TEXT):
        surface.blit((font or self.font).render(text, True, color), pos)

    def panel(self, surface, rect, alpha=150):
        """Напівпрозора підкладка; поверхні створюються один раз і кешуються."""
        key = (rect.size, alpha)
        if key not in self._shades:
            self._shades[key] = pygame.Surface(rect.size, pygame.SRCALPHA)
            self._shades[key].fill((0, 0, 0, alpha))
        surface.blit(self._shades[key], rect.topleft)

    def draw(self, surface, t: float, duration: float, playing: bool, enabled: list[bool], message: str = ""):
        song = self.song
        self.panel(surface, pygame.Rect(0, 0, W, 44))
        self.text(surface, f"MIDI-анімація · {song.name}", (16, 12), self.title)
        numerator, denominator = song.meter
        info = f"{song.bpm_at(t):.0f} BPM · {numerator}/{denominator} · доріжок: {len(song.tracks)} · нот: {len(song.notes)}"
        image = self.font.render(info, True, DIM)
        surface.blit(image, (W - image.get_width() - 16, 14))

        legend_bottom = self.draw_legend(surface, enabled)
        for k, warning in enumerate(song.warnings):           # під легендою, щоб не перекривати панелі
            self.text(surface, warning, (16, legend_bottom + 8 + 20 * k), color=(255, 120, 120))
        self.draw_log(surface, t, enabled)

        self.panel(surface, pygame.Rect(0, H - 62, W, 62))
        pygame.draw.rect(surface, (60, 66, 90), BAR, border_radius=4)
        done = BAR.copy()
        done.width = int(BAR.width * min(1.0, t / duration))
        pygame.draw.rect(surface, (255, 196, 87), done, border_radius=4)
        state = "відтворення" if playing else "пауза"
        self.text(surface, f"{clock(t)} / {clock(duration)}   {state}", (BAR.right + 20, BAR.y - 6))
        self.text(surface, HINT, (40, H - 28), self.small, DIM)
        if message:                                           # помилка відкриття файлу — червона плашка
            image = self.font.render(message, True, (255, 240, 240))
            plate = image.get_rect(center=(W // 2, H - 100)).inflate(32, 18)
            pygame.draw.rect(surface, (160, 40, 55), plate, border_radius=8)
            surface.blit(image, image.get_rect(center=plate.center))

    def draw_legend(self, surface, enabled) -> int:
        """Доріжка → колір і тип об'єкта; кружок збільшується, коли доріжка звучить.
        Повертає нижній край панелі."""
        rect = pygame.Rect(12, 54, 480, 14 + 24 * len(self.song.tracks))
        self.panel(surface, rect, 120)
        for i, track in enumerate(self.song.tracks):
            y = 62 + 24 * i
            on = enabled[i]
            size = 8 if i in self.visual.sounding else 5
            pygame.draw.circle(surface, self.visual.colors[i] if on else MUTED, (32, y + 9), size)
            label = f"{i + 1}  {track.name} — {ROLE_NAMES[track.role]} → {OBJECTS[track.role]}"
            self.text(surface, label + ("" if on else "  (вимкнено)"), (48, y), color=TEXT if on else MUTED)
        return rect.bottom

    def draw_log(self, surface, t, enabled):
        """Останні події note_on і що з них вийшло на екрані."""
        recent = []
        for track, starts in zip(self.song.tracks, self.visual.track_starts):
            if enabled[track.index]:                          # з кожної доріжки — її останні ноти
                i = bisect.bisect_right(starts, t)
                recent += track.notes[max(0, i - LOG_LINES):i]
        events = sorted(recent, key=lambda n: (n.start, n.track, n.pitch), reverse=True)[:LOG_LINES]

        rect = pygame.Rect(W - 520, 54, 508, 40 + 20 * LOG_LINES)
        self.panel(surface, rect, 120)
        self.text(surface, "Подія MIDI → об'єкт анімації", (rect.x + 12, rect.y + 8), self.bold)
        for k, note in enumerate(events):
            color = self.visual.colors[note.track] if t - note.start < 0.3 else DIM   # свіжі події — кольором
            self.text(surface, f"{clock(note.start)}  {self.visual.describe(note)}",
                      (rect.x + 12, rect.y + 32 + 20 * k), self.small, color)
