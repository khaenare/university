"""Експерименти: для кожного зображення і рівня стиснення — PSNR методів DCT і DWT.

Запуск:  python experiments.py
Результати в папці results:
    results.md, results.csv — таблиця
    psnr.png                — графік PSNR від частки збережених коефіцієнтів
    <зображення>.png        — Оригінал | DCT | DWT на трьох рівнях стиснення
"""
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")                                 # без вікна — лише збереження у файли
import matplotlib.pyplot as plt  # noqa: E402

from compression.codec import analyze, compress, format_db, load_image  # noqa: E402

HERE = Path(__file__).parent
RESULTS = HERE / "results"
FRACTIONS = [0.01, 0.02, 0.05, 0.10, 0.20]           # ліміт: частка збережених коефіцієнтів
SHOWN = [0.01, 0.05, 0.20]                            # рівні для візуального порівняння
METHODS = ("DCT", "DWT")


def main():
    RESULTS.mkdir(exist_ok=True)
    images = {p.stem: load_image(p) for p in sorted((HERE / "images").glob("*.png"))}
    rows = []
    for name, image in images.items():
        coeffs = {m: analyze(image, m) for m in METHODS}          # пряме перетворення — один раз
        results = {(f, m): compress(image, m, f, coeffs[m]) for f in FRACTIONS for m in METHODS}
        for fraction in FRACTIONS:
            dct, dwt = results[fraction, "DCT"], results[fraction, "DWT"]
            rows.append(dict(image=name, percent=fraction * 100,
                             kept_dct=dct.kept, kept_dwt=dwt.kept, ratio_dct=dct.ratio, ratio_dwt=dwt.ratio,
                             psnr_dct=dct.psnr, psnr_dwt=dwt.psnr))
        save_comparison(name, image, results)

    with open(RESULTS / "results.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)

    lines = ["| Зображення | Ліміт, % | Збережено DCT (стиснення) | Збережено DWT (стиснення) "
             "| PSNR DCT, дБ | PSNR DWT, дБ | Краще |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        dct, dwt = r["psnr_dct"], r["psnr_dwt"]
        diff = dct - dwt if dct != dwt else 0.0              # ∞ − ∞ не рахуємо
        better = "≈" if abs(diff) < 0.05 else "DCT" if diff > 0 else "DWT"
        lines.append(f"| {r['image']} | {r['percent']:g} | {r['kept_dct']} ({r['ratio_dct']:.0f} : 1) "
                     f"| {r['kept_dwt']} ({r['ratio_dwt']:.0f} : 1) | {format_db(dct)} | {format_db(dwt)} | {better} |")
    (RESULTS / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    save_plot(rows, images)
    print("\n".join(lines))


def save_comparison(name, image, results):
    """Сітка: рядки — рівні стиснення, стовпці — Оригінал | DCT | DWT."""
    fig, axes = plt.subplots(len(SHOWN), 3, figsize=(12, 4.2 * len(SHOWN)))
    for row, fraction in zip(axes, SHOWN):
        row[0].imshow(image, cmap="gray", vmin=0, vmax=255)
        row[0].set_title("Оригінал")
        for ax, method in zip(row[1:], METHODS):
            result = results[fraction, method]
            ax.imshow(result.restored, cmap="gray", vmin=0, vmax=255)
            ax.set_title(f"{method}, {fraction:.0%} коефіцієнтів: PSNR {format_db(result.psnr)} дБ")
        for ax in row:
            ax.axis("off")
    fig.tight_layout()
    fig.savefig(RESULTS / f"{name}.png", dpi=110)
    plt.close(fig)


def save_plot(rows, images):
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for index, name in enumerate(images):
        color = f"C{index}"
        data = [r for r in rows if r["image"] == name and float("inf") not in (r["psnr_dct"], r["psnr_dwt"])]
        x = [r["percent"] for r in data]
        ax.plot(x, [r["psnr_dct"] for r in data], "-o", color=color, label=f"{name} — DCT")
        ax.plot(x, [r["psnr_dwt"] for r in data], "--s", color=color, label=f"{name} — DWT")
    ax.set_xscale("log")
    ax.set_xticks([p * 100 for p in FRACTIONS], [f"{p:.0%}" for p in FRACTIONS])
    ax.set_xlabel("Частка збережених коефіцієнтів")
    ax.set_ylabel("PSNR, дБ")
    ax.set_title("Якість відновлення: DCT (суцільна) і DWT Хаара (пунктир)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(RESULTS / "psnr.png", dpi=120)
    plt.close(fig)


if __name__ == "__main__":
    main()
