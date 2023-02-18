
import numpy as np
from numba import jit, njit

from .base import BaseReplaser
from .base import Image
from .base import dt_now


@jit(nopython=True)
def get_color_hash(r: int, g: int, b: int, size: int) -> int:
    """Hash function for a color value.
    """
    result = 1 + int(r * 10 + g * 100 + b * 1000 + (r + g + b) ** 2) % (size - 1)  # noqa
    return result


@njit
def search_top_frequency(
    w: int,
    h: int,
    img: np.array,
    index: np.array,
    index_size: int,
    top_frequency: float
) -> np.array:
    """Index with frequency of color for pixel.
    """
    i = -1
    delta = w * h
    for x in range(w):
        for y in range(h):
            i += 1
            r = int(img[i])
            g = int(img[i + delta])
            b = int(img[i + delta * 2])
            index_i = get_color_hash(r, g, b, index_size)
            index[index_i] = index[index_i] + 1

    top_size = 0
    p = float(w * h)
    for i in range(index_size):
        if (index[i]) / p * 100.0 > top_frequency:
            top_size += 1

    stat = np.zeros((4, top_size), dtype=np.uint32)
    top_size = -1
    for i in range(index_size):
        if (index[i]) / p * 100.0 > top_frequency:
            top_size += 1
            stat[3, top_size] = i

    _, top_size = stat.shape

    i = -1
    for x in range(w):
        for y in range(h):
            i += 1
            r = int(img[i])
            g = int(img[i + delta])
            b = int(img[i + delta * 2])
            index_i = get_color_hash(r, g, b, index_size)
            if (index[index_i]) / p * 100.0 > top_frequency:
                for t in range(top_size):
                    if stat[3, t] == index_i:
                        stat[0, t] = r
                        stat[1, t] = g
                        stat[2, t] = b
                        break

    return stat[:3, :].astype(np.uint8)


@njit
def replace_bg(
    w: int,
    h: int,
    img: np.array,
    colors: np.array,
    color_count: int,
    new_r: int,
    new_g: int,
    new_b: int,
    threshold: float
) -> int:
    """Prepare result array.
    """
    white = np.array([new_r, new_g, new_b], dtype=np.uint8)
    count = 0
    i = -1
    delta = w * h
    change = False
    c_s = 255.0
    a_lim = 0.0
    th = threshold / 100.0
    for _ in range(w):
        for _ in range(h):
            i += 1
            r = img[i]
            g = img[i + delta]
            b = img[i + delta * 2]

            change = False
            for c_i in range(color_count):
                c_r = colors[0, c_i]
                c_g = colors[1, c_i]
                c_b = colors[2, c_i]

                a_lim = (
                    (
                        float(r - c_r if r > c_r else c_r - r) / c_s
                    ) + (
                        float(g - c_g if g > c_g else c_g - g) / c_s
                    ) + (
                        float(b - c_b if b > c_b else c_b - b) / c_s
                    )
                ) / 3.0
                if th >= a_lim:
                    change = True
                    break

            if change:
                count += 1
                for c in range(3):
                    img[i + delta * c] = white[c]

    return int(float(count) / float(delta) * 100.0 + 0.5)


def apply(
    w: int,
    h: int,
    img: np.array,
    new_r: int,
    new_g: int,
    new_b: int,
    area_frequency_limit: float,
    threshold: float
) -> float:
    index_size = 32000
    index = np.zeros((index_size,), dtype=np.int32)
    colors = search_top_frequency(
        w, h, img, index, index_size, area_frequency_limit
    )
    _, color_n = colors.shape
    return replace_bg(
        w, h, img, colors, color_n, new_r, new_g, new_b, threshold
    )


class Replaser(BaseReplaser):

    def apply(self, operation_repeat: int):
        self.operation_repeat = operation_repeat
        data = np.asarray(self.rgb_image.convert("RGB"))
        h, w, color = data.shape
        self.w = w
        self.h = h
        new_r, new_g, new_b = self.new_color
        src = data.reshape((w * h * color,), order="F").astype("uint8")
        replaced = 0
        fl = self.area_frequency_limit
        threshold = self.color_threshold
        self.operation_time = 0
        for _ in range(operation_repeat):
            img = src.copy()
            start_time = dt_now()
            replaced = apply(
                w, h, img, new_r, new_g, new_b, float(fl), float(threshold)
            )
            self.operation_time += dt_now() - start_time

        self.replaced = replaced
        img_res = img.reshape((h, w, 3), order="F")
        self.result_image = Image.fromarray(img_res, mode="RGB")
