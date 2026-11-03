"""Відтворення звуку синхронно з анімацією.

Годинник анімації — реальний час (time.perf_counter), а не кількість кадрів:
при запуску звуку з позиції p запам'ятовуємо t0 = зараз − p, і поточна
позиція = зараз − t0. Тому анімація не відстає від звуку, навіть якщо FPS
просідає. Перемотування — це запуск звуку з потрібного відліку масиву.
"""
from __future__ import annotations

import time

import numpy as np
import pygame

from .synth import SR

BUFFER = 1024              # розмір буфера міксера, відліків
LATENCY = BUFFER / SR      # звук доходить до динаміків на один буфер пізніше за запуск (≈23 мс);
                           # додаткову затримку пристрою (наприклад, Bluetooth) програма знати не може


class AudioPlayer:
    def __init__(self):
        # pygame.init() уже відкриває міксер з типовими параметрами, а повторний init() їх
        # не змінює — тому перезапускаємо. allowedchanges=0: SDL сам перетворює звук під
        # пристрій, а програма гарантовано працює з 44,1 кГц стерео, як і синтезатор.
        pygame.mixer.quit()
        pygame.mixer.init(frequency=SR, size=-16, channels=2, buffer=BUFFER, allowedchanges=0)
        self._channel = pygame.mixer.Channel(0)    # завжди один і той самий канал
        self.samples = np.zeros((1, 2), dtype=np.int16)
        self.duration = 0.0
        self.position = 0.0       # позиція на паузі, с
        self.playing = False
        self._t0 = 0.0

    def load(self, samples: np.ndarray):
        self.pause()
        self.samples = samples
        self.duration = len(samples) / SR
        self.position = 0.0

    def replace(self, samples: np.ndarray):
        """Новий мікс (наприклад, після вимкнення доріжки) з тієї самої позиції."""
        now = self.time()
        self.samples = samples
        if self.playing:
            self._start(now)

    def time(self) -> float:
        if self.playing:
            return min(max(0.0, time.perf_counter() - self._t0), self.duration)
        return self.position

    def toggle(self):
        if self.playing:
            self.pause()
        else:
            self._start(0.0 if self.position >= self.duration else self.position)

    def pause(self):
        if self.playing:
            self.position = self.time()
            self.playing = False
            self._channel.stop()

    def seek(self, seconds: float):
        seconds = min(max(0.0, seconds), self.duration)
        if self.playing:
            self._start(seconds)
        else:
            self.position = seconds

    def _start(self, seconds: float):
        offset = min(int(seconds * SR), len(self.samples) - 1)
        sound = pygame.sndarray.make_sound(np.ascontiguousarray(self.samples[offset:]))
        self._channel.play(sound)                  # play() на тому самому каналі зупиняє попередній звук
        self._t0 = time.perf_counter() - seconds + LATENCY
        self.playing = True
