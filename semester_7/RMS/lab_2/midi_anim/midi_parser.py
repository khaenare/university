"""Читання MIDI-файлу та перетворення подій на ноти з часом у секундах.

MIDI зберігає час подій у тіках, причому кожна подія містить не абсолютний
час, а різницю з попередньою (delta-time). Темп задається окремими подіями
set_tempo (мікросекунди на чверть) і може змінюватися посеред пісні.
Тому парсер:
  1) переводить delta-time в абсолютні тіки для кожної доріжки;
  2) будує карту темпу з усіх подій set_tempo;
  3) перетворює тіки на секунди з урахуванням змін темпу;
  4) зводить пари note_on / note_off у ноти з початком, кінцем і velocity.
"""
from __future__ import annotations

import bisect
from dataclasses import dataclass, field
from pathlib import Path

import mido

DRUM_CHANNEL = 9          # 10-й канал General MIDI (нумерація з нуля) — ударні
DEFAULT_TEMPO = 500_000   # 120 BPM — стандартний темп, якщо у файлі немає set_tempo
MIN_NOTE = 0.05           # мінімальна тривалість ноти, с (щоб «нульові» ноти було видно)
DRUM_NOTE = 0.3           # найбільша тривалість удару, с: для ударних тривалість у MIDI не важлива,
                          # а note_off у них часто взагалі немає — тоді удар «тривав» би до кінця пісні

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_name(pitch: int) -> str:
    """60 → 'C4' (до першої октави)."""
    return f"{NOTE_NAMES[pitch % 12]}{pitch // 12 - 1}"


def drum_kind(pitch: int) -> str:
    """Тип удару за картою ударних General MIDI — спільний для звуку й анімації."""
    if pitch in (35, 36):
        return "kick"           # бочка
    if pitch in (37, 38, 39, 40):
        return "snare"          # малий барабан, side stick, плеск
    return "hat"                # хай-хет, маракаси, тарілки та інші


@dataclass(frozen=True)
class Note:
    track: int        # індекс доріжки в Song.tracks
    channel: int
    pitch: int        # 0–127
    velocity: int     # 1–127 — сила натискання
    start: float      # початок, с
    end: float        # кінець, с

    @property
    def duration(self) -> float:
        return self.end - self.start


@dataclass
class Track:
    index: int
    name: str
    channel: int
    program: int | None                 # інструмент General MIDI (0–127) або None
    notes: list[Note] = field(default_factory=list)
    role: str = "harmony"               # drums / bass / melody / harmony — визначає тип анімації

    @property
    def is_drums(self) -> bool:
        return self.channel == DRUM_CHANNEL

    @property
    def mean_pitch(self) -> float:
        return sum(n.pitch for n in self.notes) / len(self.notes)

    @property
    def max_polyphony(self) -> int:
        """Найбільша кількість нот, що звучать одночасно."""
        events = sorted([(n.start, 1) for n in self.notes] + [(n.end, -1) for n in self.notes])
        current = best = 0
        for _, delta in events:
            current += delta
            best = max(best, current)
        return best


@dataclass
class Song:
    path: Path
    tracks: list[Track]
    notes: list[Note]          # усі ноти, відсортовані за початком
    meter: tuple[int, int]     # розмір такту, наприклад (6, 8)
    tempos: list[tuple[float, float]]   # зміни темпу: (секунда, BPM)
    duration: float            # кінець останньої ноти, с
    warnings: list[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.path.name

    def bpm_at(self, t: float) -> float:
        """Темп, що діє в момент t."""
        i = bisect.bisect_right([second for second, _ in self.tempos], t) - 1
        return self.tempos[max(i, 0)][1]


class TempoMap:
    """Перетворення абсолютних тіків на секунди з урахуванням змін темпу.

    Пісня ділиться на відрізки зі сталим темпом. Для кожного відрізка
    запам'ятовуємо тік і секунду його початку — тоді будь-який тік
    переводиться в секунди за одним бінарним пошуком.
    """

    def __init__(self, tempo_events: list[tuple[int, int]], ticks_per_beat: int):
        self.ticks_per_beat = ticks_per_beat
        self.ticks: list[int] = [0]
        self.tempos: list[int] = [DEFAULT_TEMPO]
        self.seconds: list[float] = [0.0]
        for tick, tempo in sorted(tempo_events, key=lambda e: e[0]):   # стабільне сортування
            if tick == self.ticks[-1]:            # кілька подій в один момент — діє остання
                self.tempos[-1] = tempo
                continue
            self.seconds.append(self.to_seconds(tick))
            self.ticks.append(tick)
            self.tempos.append(tempo)

    def to_seconds(self, tick: int) -> float:
        i = bisect.bisect_right(self.ticks, tick) - 1
        seconds_per_tick = self.tempos[i] / 1_000_000 / self.ticks_per_beat
        return self.seconds[i] + (tick - self.ticks[i]) * seconds_per_tick


def _pair_notes(events: list[tuple[int, mido.Message]]):
    """Зводить note_on / note_off у ноти. Повертає ноти в тіках і перші програми каналів."""
    open_notes: dict[tuple[int, int], list[tuple[int, int]]] = {}
    notes = []        # (channel, pitch, velocity, start_tick, end_tick)
    programs: dict[int, int] = {}
    last_tick = 0
    for tick, msg in events:
        last_tick = tick
        if msg.type == "program_change":
            programs.setdefault(msg.channel, msg.program)
        elif msg.type == "note_on" and msg.velocity > 0:
            open_notes.setdefault((msg.channel, msg.note), []).append((tick, msg.velocity))
        elif msg.type in ("note_off", "note_on"):          # note_on з velocity 0 — теж кінець ноти
            stack = open_notes.get((msg.channel, msg.note))
            if stack:
                start, velocity = stack.pop(0)             # першою закривається найстаріша нота
                notes.append((msg.channel, msg.note, velocity, start, tick))
    for (channel, pitch), stack in open_notes.items():     # ноти без note_off — до кінця доріжки
        for start, velocity in stack:
            notes.append((channel, pitch, velocity, start, max(last_tick, start)))
    return notes, programs


def _assign_roles(tracks: list[Track]) -> None:
    """Роль доріжки визначає тип анімації: ударні, бас, мелодія чи гармонія."""
    for track in tracks:
        if track.is_drums:
            track.role = "drums"
        elif (track.program is not None and track.program // 8 == 4) or track.mean_pitch < 48:
            track.role = "bass"
    melodic = [t for t in tracks if t.role == "harmony"]
    if melodic:
        # мелодія — найвища за звучанням доріжка, переважно одноголосна
        lead = max(melodic, key=lambda t: (t.max_polyphony <= 2, t.mean_pitch))
        lead.role = "melody"


def load_song(path: str | Path) -> Song:
    """Читає MIDI-файл. Будь-яка проблема з файлом → ValueError із зрозумілим повідомленням."""
    path = Path(path)
    try:
        midi = mido.MidiFile(path)
    except FileNotFoundError:
        raise ValueError(f"Файл не знайдено: {path.name}") from None
    except (OSError, EOFError, ValueError, KeyError, IndexError) as error:
        raise ValueError(f"«{path.name}» пошкоджений або не є MIDI-файлом") from error
    tempo_events, signatures, raw_tracks = [], [], []
    for index, midi_track in enumerate(midi.tracks):
        tick, events = 0, []
        for msg in midi_track:
            tick += msg.time                               # delta-time → абсолютний тік
            if msg.type == "set_tempo":
                tempo_events.append((tick, msg.tempo))
            elif msg.type == "time_signature":
                signatures.append((tick, msg.numerator, msg.denominator))
            events.append((tick, msg))
        raw_tracks.append((midi_track.name.strip() or f"Доріжка {index + 1}", events))

    tempo = TempoMap(tempo_events, midi.ticks_per_beat)
    tracks: list[Track] = []
    for name, events in raw_tracks:
        notes, programs = _pair_notes(events)
        channels = sorted({n[0] for n in notes})
        for channel in channels:                           # формат 0: ділимо доріжку за каналами
            track = Track(index=len(tracks), channel=channel, program=programs.get(channel),
                          name=name if len(channels) == 1 else f"{name} · канал {channel + 1}")
            for ch, pitch, velocity, start_tick, end_tick in notes:
                if ch != channel:
                    continue
                start = tempo.to_seconds(start_tick)
                end = max(tempo.to_seconds(end_tick), start + MIN_NOTE)
                if ch == DRUM_CHANNEL:
                    end = min(end, start + DRUM_NOTE)
                track.notes.append(Note(track.index, ch, pitch, velocity, start, end))
            track.notes.sort(key=lambda n: (n.start, n.pitch))
            tracks.append(track)

    if not tracks:
        raise ValueError(f"У файлі «{path.name}» немає жодної ноти")
    _assign_roles(tracks)

    all_notes = sorted((n for t in tracks for n in t.notes), key=lambda n: (n.start, n.track, n.pitch))
    warnings = []
    if len(tracks) < 2:
        warnings.append("У файлі лише одна доріжка з нотами — за умовою потрібно щонайменше дві")
    return Song(path=path, tracks=tracks, notes=all_notes,
                meter=min(signatures)[1:] if signatures else (4, 4),       # найраніший time_signature
                tempos=[(s, mido.tempo2bpm(t)) for s, t in zip(tempo.seconds, tempo.tempos)],
                duration=max(n.end for n in all_notes),
                warnings=warnings)
