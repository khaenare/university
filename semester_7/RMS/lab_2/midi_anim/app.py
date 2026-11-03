"""Головне вікно: цикл кадрів, керування з клавіатури й миші."""
from __future__ import annotations

import time
from pathlib import Path

import pygame

from .audio import AudioPlayer
from .hud import BAR, Hud
from .midi_parser import load_song
from .synth import master_gain, mix, render_stems
from .visuals import H, W, Visualizer

MESSAGE_SECONDS = 6       # скільки показується повідомлення про помилку


class App:
    def __init__(self, midi_path):
        pygame.init()
        self.audio = AudioPlayer()
        self.message, self.message_time = "", 0.0
        self.load(midi_path)                  # некоректний файл → ValueError ще до відкриття вікна
        self.screen = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()

    def load(self, path):
        """Нова пісня. Якщо файл некоректний, load_song кидає ValueError і поточна пісня лишається."""
        self.song = load_song(path)
        self.stems = render_stems(self.song)
        self.gain = master_gain(self.stems)
        self.enabled = [True] * len(self.song.tracks)
        self.visual = Visualizer(self.song)
        self.hud = Hud(self.song, self.visual)
        self.audio.load(mix(self.stems, self.enabled, self.gain))
        self.audio.toggle()                                   # одразу починаємо відтворення
        self.message = ""
        pygame.display.set_caption(f"MIDI-анімація — {self.song.name}")

    def open_file(self, path: str):
        """Файл, перетягнутий у вікно: перевіряємо тип і показуємо помилку на екрані."""
        if not path.lower().endswith((".mid", ".midi")):
            self.show_message(f"«{Path(path).name}» — не MIDI: підтримуються лише файли .mid і .midi")
            return
        try:
            self.load(path)
        except ValueError as error:
            self.show_message(str(error))

    def show_message(self, text: str):
        self.message, self.message_time = text, time.perf_counter()

    def run(self):
        while self.handle_events():
            t = self.audio.time()
            if self.audio.playing and t >= self.audio.duration:
                self.audio.pause()
            message = self.message if time.perf_counter() - self.message_time < MESSAGE_SECONDS else ""
            self.visual.draw(self.screen, t, self.enabled)
            self.hud.draw(self.screen, t, self.audio.duration, self.audio.playing, self.enabled, message)
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return False
            if event.type == pygame.KEYDOWN:
                self.on_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and BAR.inflate(0, 20).collidepoint(event.pos):
                self.audio.seek((event.pos[0] - BAR.x) / BAR.width * self.audio.duration)
            elif event.type == pygame.DROPFILE:
                self.open_file(event.file)
        return True

    def on_key(self, key):
        if key == pygame.K_SPACE:
            self.audio.toggle()
        elif key == pygame.K_LEFT:
            self.audio.seek(self.audio.time() - 5)
        elif key == pygame.K_RIGHT:
            self.audio.seek(self.audio.time() + 5)
        elif pygame.K_1 <= key <= pygame.K_9 and key - pygame.K_1 < len(self.enabled):
            i = key - pygame.K_1                               # вимкнути/увімкнути доріжку: звук і об'єкти
            self.enabled[i] = not self.enabled[i]
            self.audio.replace(mix(self.stems, self.enabled, self.gain))
