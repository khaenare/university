"""Тести власних реалізацій DCT і DWT, механізму стиснення, PSNR і читання зображень."""
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from compression.codec import SIZE, compress, keep_largest, load_image, psnr
from compression.dct import BLOCK, C, dct2, group_by_frequency, idct2
from compression.haar import dwt2, idwt2


def random_image(shape, seed=0):
    """Окремий генератор у кожному тесті — дані не залежать від порядку тестів."""
    return np.random.default_rng(seed).uniform(0, 255, shape)


def naive_dct_block(block):
    """DCT-II за формулою з подвійною сумою — незалежна перевірка матричної версії."""
    n = len(block)
    out = np.zeros((n, n))
    for u in range(n):
        for v in range(n):
            au = math.sqrt((1 if u == 0 else 2) / n)
            av = math.sqrt((1 if v == 0 else 2) / n)
            out[u, v] = au * av * sum(block[x, y] * math.cos(math.pi * (2 * x + 1) * u / (2 * n))
                                      * math.cos(math.pi * (2 * y + 1) * v / (2 * n))
                                      for x in range(n) for y in range(n))
    return out


class DctTest(unittest.TestCase):
    def test_matrix_is_orthonormal(self):
        np.testing.assert_allclose(C @ C.T, np.eye(BLOCK), atol=1e-12)

    def test_matches_definition(self):
        block = random_image((BLOCK, BLOCK)) - 128
        np.testing.assert_allclose(dct2(block), naive_dct_block(block), atol=1e-9)

    def test_constant_block_has_only_dc(self):
        coeffs = dct2(np.full((8, 8), 10.0))
        self.assertAlmostEqual(coeffs[0, 0], 80.0)               # DC = 8 · середнє
        self.assertAlmostEqual(np.abs(coeffs).sum() - 80.0, 0.0, places=9)

    def test_perfect_reconstruction(self):
        image = random_image((64, 96))
        np.testing.assert_allclose(idct2(dct2(image)), image, atol=1e-9)

    def test_group_by_frequency_layout(self):
        coeffs = np.zeros((16, 24))                               # 2 × 3 блоки
        coeffs[8 + 3, 16 + 4] = 7                                 # блок (1, 2), частота (3, 4)
        grouped = group_by_frequency(coeffs)
        self.assertEqual(grouped[3 * 2 + 1, 4 * 3 + 2], 7)        # частота (3, 4) → своя мініатюра, місце блоку (1, 2)
        self.assertEqual(np.count_nonzero(grouped), 1)

    def test_size_must_be_multiple_of_8(self):
        with self.assertRaisesRegex(ValueError, "ділитися на 8"):
            dct2(np.zeros((10, 16)))


class HaarTest(unittest.TestCase):
    def test_one_level_by_hand(self):
        # рядки: (1+2)/√2, (1−2)/√2 …; стовпці — так само → LL=5, HL=−1, LH=−2, HH=0
        np.testing.assert_allclose(dwt2(np.array([[1.0, 2.0], [3.0, 4.0]]), levels=1), [[5, -1], [-2, 0]])

    def test_perfect_reconstruction(self):
        image = random_image((64, 128))
        for levels in range(0, 6):
            with self.subTest(levels=levels):
                np.testing.assert_allclose(idwt2(dwt2(image, levels), levels), image, atol=1e-9)

    def test_energy_is_preserved(self):
        image = random_image((32, 32))
        self.assertAlmostEqual(np.sum(dwt2(image, 3) ** 2) / np.sum(image ** 2), 1.0, places=12)

    def test_size_must_fit_levels(self):
        for transform in (dwt2, idwt2):
            with self.subTest(transform=transform.__name__), self.assertRaisesRegex(ValueError, "ділитися на 32"):
                transform(np.zeros((48, 64)), levels=5)


class CompressionTest(unittest.TestCase):
    def test_keep_largest(self):
        coeffs = np.array([[5.0, -9.0], [1.0, 3.0]])
        kept = keep_largest(coeffs, 0.5)                          # 2 з 4 найбільших за модулем
        np.testing.assert_array_equal(kept, [[5.0, -9.0], [0.0, 0.0]])

    def test_invalid_fraction(self):
        for fraction in (0, -0.1, 1.5):
            with self.subTest(fraction=fraction), self.assertRaises(ValueError):
                keep_largest(np.ones((4, 4)), fraction)

    def test_kept_equals_limit_for_detailed_image(self):
        image = random_image((64, 64))
        for method in ("DCT", "DWT"):
            result = compress(image, method, 0.1)
            self.assertEqual(result.kept, round(0.1 * image.size))
            self.assertEqual(result.kept, np.count_nonzero(result.coeffs))

    def test_zeros_are_not_counted(self):
        image = np.full((64, 64), 128.0)                          # однотонне: усі коефіцієнти нульові
        image[:32] = 0                                            # дві однотонні половини
        for method in ("DCT", "DWT"):
            result = compress(image, method, 1.0)
            self.assertLess(result.kept, image.size)              # нулі не зараховуються як збережені
            self.assertEqual(result.psnr, float("inf"))
        self.assertEqual(compress(np.full((64, 64), 128.0), "DWT", 0.5).kept, 0)

    def test_full_fraction_is_lossless(self):
        image = np.round(random_image((64, 64)))
        for method in ("DCT", "DWT"):
            np.testing.assert_array_equal(compress(image, method, 1.0).restored, image)

    def test_more_coefficients_better_quality(self):
        x, y = np.meshgrid(np.arange(64), np.arange(64))
        image = 128 + 60 * np.sin(x / 5) * np.cos(y / 7)
        for method in ("DCT", "DWT"):
            scores = [compress(image, method, f).psnr for f in (0.01, 0.05, 0.2)]
            self.assertEqual(scores, sorted(scores))


class PsnrTest(unittest.TestCase):
    def test_known_value(self):
        self.assertAlmostEqual(psnr(np.zeros((4, 4)), np.ones((4, 4))), 20 * math.log10(255))   # MSE = 1

    def test_identical(self):
        self.assertEqual(psnr(np.ones((4, 4)), np.ones((4, 4))), float("inf"))


class LoadImageTest(unittest.TestCase):
    def setUp(self):
        self.folder = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def test_color_non_square_becomes_gray_512(self):
        path = self.folder / "color.png"
        Image.new("RGB", (800, 300), (255, 0, 0)).save(path)
        image = load_image(path)
        self.assertEqual(image.shape, (SIZE, SIZE))
        self.assertAlmostEqual(image.mean(), 76, delta=1)          # червоний → яскравість 0,299 · 255

    def test_16_bit_is_scaled_not_clipped(self):
        path = self.folder / "gradient16.png"
        Image.fromarray(np.tile(np.linspace(0, 65535, 256).astype(np.uint16), (256, 1))).save(path)
        image = load_image(path)
        self.assertAlmostEqual(image.mean(), 127.5, delta=3)       # не біле зображення
        self.assertLess(image.min(), 5)

    def test_transparency_on_white(self):
        path = self.folder / "transparent.png"
        Image.new("RGBA", (64, 64), (0, 0, 0, 0)).save(path)       # повністю прозорий чорний
        self.assertEqual(load_image(path).min(), 255)

    def test_invalid_file(self):
        path = self.folder / "not_image.png"
        path.write_text("це не зображення", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "не вдалося відкрити"):
            load_image(path)


if __name__ == "__main__":
    unittest.main()
