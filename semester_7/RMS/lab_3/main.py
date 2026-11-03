"""Лабораторна робота №3: стиснення зображень з втратами — DCT і DWT (Хаар).

Запуск:  python main.py [зображення …]
Без аргументів відкриваються тестові зображення з папки images.
Повзунок задає частку збережених коефіцієнтів, перемикач — зображення.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import RadioButtons, Slider

from compression.codec import analyze, compress, format_db, load_image
from compression.dct import group_by_frequency
from compression.haar import LEVELS

IMAGES = Path(__file__).parent / "images"


def thousands(n: int) -> str:
    """262144 → '262 144'."""
    return f"{n:,}".replace(",", " ")


class Viewer:
    def __init__(self, images: dict[str, np.ndarray]):
        self.images = images
        self.current = next(iter(images))
        self.forward: dict[tuple[str, str], np.ndarray] = {}   # кеш прямого перетворення
        self.fig = plt.figure("Стиснення зображень: DCT і DWT", figsize=(14, 9))

        # верхній ряд: оригінал і відновлені зображення; нижній — збережені коефіцієнти
        top = [self.fig.add_axes((0.02 + 0.325 * i, 0.47, 0.31, 0.45)) for i in range(3)]
        bottom = [self.fig.add_axes((0.02 + 0.325 * i, 0.09, 0.31, 0.32)) for i in (1, 2)]
        empty = np.zeros((512, 512))
        self.pictures = [ax.imshow(empty, cmap="gray", vmin=0, vmax=255) for ax in top]
        self.maps = [ax.imshow(empty, cmap="magma") for ax in bottom]
        self.titles = [ax.set_title("") for ax in top + bottom]
        for ax in top + bottom:
            ax.axis("off")

        self.radio = RadioButtons(self.fig.add_axes((0.03, 0.24, 0.27, 0.19)), list(images))
        self.radio.on_clicked(self.select)
        self.info = self.fig.text(0.03, 0.08, "", fontsize=10, va="bottom")
        self.slider = Slider(self.fig.add_axes((0.25, 0.025, 0.55, 0.03)), "Збережено коефіцієнтів, %",
                             0.5, 50, valinit=5, valstep=0.5)
        self.slider.on_changed(lambda _: self.update())
        self.update()

    def select(self, name):
        self.current = name
        self.update()

    def coefficients(self, method: str) -> np.ndarray:
        """Пряме перетворення залежить лише від зображення — рахуємо його один раз."""
        key = (self.current, method)
        if key not in self.forward:
            self.forward[key] = analyze(self.images[self.current], method)
        return self.forward[key]

    def update(self):
        image = self.images[self.current]
        fraction = self.slider.val / 100
        self.pictures[0].set_data(image)
        self.titles[0].set_text("Оригінал")
        lines = [f"Ліміт: {fraction:.1%} з {thousands(image.size)} коефіцієнтів"]
        for i, method in enumerate(("DCT", "DWT")):
            result = compress(image, method, fraction, self.coefficients(method))
            self.pictures[i + 1].set_data(result.restored)
            self.titles[i + 1].set_text(f"{method}: PSNR = {format_db(result.psnr)} дБ")
            shown = group_by_frequency(result.coeffs) if method == "DCT" else result.coeffs
            values = np.log1p(np.abs(shown))                    # логарифм — щоб було видно і малі значення
            self.maps[i].set_data(values)
            self.maps[i].set_clim(0, values.max() or 1)         # шкала за фактичними значеннями
            lines.append(f"{method}: збережено {thousands(result.kept)}, стиснення {result.ratio:.1f} : 1")
        lines.append("(за кількістю ненульових коефіцієнтів, не розміром файлу)")
        self.titles[3].set_text("Збережені коефіцієнти DCT (згруповано за частотами)")
        self.titles[4].set_text(f"Збережені коефіцієнти DWT (Хаар, {LEVELS} рівнів)")
        self.info.set_text("\n".join(lines))
        self.fig.canvas.draw_idle()


def main():
    paths = [Path(p) for p in sys.argv[1:]] or sorted(IMAGES.glob("*.png"))
    images = {}
    for path in paths:
        try:
            image = load_image(path)
        except ValueError as error:                         # некоректний файл — пропускаємо з повідомленням
            print(f"Пропущено: {error}")
            continue
        label = path.stem if path.stem not in images else f"{path.stem} ({len(images) + 1})"
        images[label] = image                               # однакові імена не затирають одне одне
    if not images:
        sys.exit("Помилка: немає жодного зображення, яке вдалося відкрити")
    viewer = Viewer(images)     # посилання обов'язкове: без нього збирач сміття знищить повзунок і перемикач
    plt.show()
    del viewer


if __name__ == "__main__":
    main()
