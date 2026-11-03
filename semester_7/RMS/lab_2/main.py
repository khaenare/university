"""MIDI-анімація — лабораторна робота №2, варіант 3.

Запуск:  python main.py [файл.mid]
Без аргументу відкривається демонстраційний файл assets/atlantic_breeze.mid.
"""
import argparse
import sys
from pathlib import Path

from midi_anim.app import App


def main():
    parser = argparse.ArgumentParser(description="Анімація на основі MIDI-файлу")
    parser.add_argument("midi", nargs="?", default=Path(__file__).parent / "assets" / "atlantic_breeze.mid",
                        help="MIDI-файл зі щонайменше двома доріжками")
    try:
        app = App(parser.parse_args().midi)
    except ValueError as error:                       # некоректний файл — повідомлення замість трасування
        sys.exit(f"Помилка: {error}")
    app.run()


if __name__ == "__main__":
    main()
