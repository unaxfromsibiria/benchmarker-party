from numba import njit

import numpy as np

from .base import BaseReplaser
from .base import Image
from .base import dt_now
from numba import types
from numba.typed import Dict


@njit
def get_color_hash(img: np.array, size: int) -> np.array:
    """Hash function for a color value.
    """
    r = img[:, :, 0]
    g = img[:, :, 1]
    b = img[:, :, 2]
    d = (r + g + b) ** 2
    result = 1 + (r * 10 + g * 100 + b * 1000 + d) % (size - 1)  # noqa
    return result.astype("int32")


@njit
def search_top_frequency(
    w: int,
    h: int,
    img: np.array,
    index_size: int,
    top_frequency: float = 1
) -> np.array:
    """Index with frequency of color for pixel.
    """
    indexes = get_color_hash(img, index_size)
    # does not works np.unique
    counts_d = Dict.empty(key_type=types.int32, value_type=types.int32)
    for i in range(h):
        for j in range(w):
            i_val = indexes[i, j]
            if i_val in counts_d:
                counts_d[i_val] += 1
            else:
                counts_d[i_val] = 1

    counts = np.zeros((len(counts_d),), dtype="int")
    values = counts.copy()
    for i, key in enumerate(counts_d):
        counts[i] = counts_d[key]
        values[i] = key

    p = w * h
    top = values[counts / p * 100.0 > top_frequency]
    top_size = top.shape[0]
    result = np.zeros((top_size, 3), dtype="uint8")
    for i, index in enumerate(top):
        done = False
        for x in range(h):
            if done:
                break
            for y in range(w):
                if indexes[x, y] == index:
                    result[i, 0] = img[x, y][0]
                    result[i, 1] = img[x, y][1]
                    result[i, 2] = img[x, y][2]
                    done = True
                    break

    return result


@njit
def replace_bg(
    w: int,
    h: int,
    img: np.array,
    colors: np.array,
    new_r: int,
    new_g: int,
    new_b: int,
    threshold: int = 10  # 15%
) -> int:
    """Prepare result array.
    """
    white = np.array([new_r, new_g, new_b], dtype="uint8")
    values = img.astype("int")
    th = threshold / 100.0
    mask = np.full((h, w), True, dtype="?")
    for color in colors:
        e = np.zeros((h, w, 3), dtype="int")
        e[:, :, 0] = color[0]
        e[:, :, 1] = color[1]
        e[:, :, 2] = color[2]
        diff = (np.abs(e - values) / 255.0).sum(axis=2) / 3.0
        mask &= (diff <= th)

    count = mask.sum()
    for i in range(h):
        for j in range(w):
            if mask[i, j]:
                img[i, j, 0] = white[0]
                img[i, j, 1] = white[1]
                img[i, j, 2] = white[2]

    delta = w * h
    return int(count / delta * 100.0 + 0.5)


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
    colors = search_top_frequency(
        w, h, img, 32000, area_frequency_limit
    )
    return replace_bg(
        w, h, img, colors, new_r, new_g, new_b, threshold
    )


class Replaser(BaseReplaser):

    def apply(self, operation_repeat: int):
        self.operation_repeat = operation_repeat
        data = np.asarray(self.rgb_image.convert("RGB"))
        h, w, color = data.shape
        self.w = w
        self.h = h
        new_r, new_g, new_b = self.new_color
        src = data.astype("uint8")
        replaced = 0
        fl = self.area_frequency_limit
        threshold = self.color_threshold
        self.operation_time = 0
        for _ in range(operation_repeat):
            img = src.copy()
            start_time = dt_now()
            replaced = apply(
                w, h, img, new_r, new_g, new_b, fl, threshold
            )
            self.operation_time += dt_now() - start_time

        self.replaced = replaced
        self.result_image = Image.fromarray(img, mode="RGB")
