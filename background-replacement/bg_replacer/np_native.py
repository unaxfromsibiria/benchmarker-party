from typing import Optional
from typing import Tuple

import numpy as np

from .base import BaseReplaser
from .base import Image
from .base import dt_now


def get_color_hash(img: np.array, size: int) -> np.array:
    """Hash function for a color value.
    """
    d = img.sum(axis=(2,)) ** 2
    r = img[:, :, 0]
    g = img[:, :, 1]
    b = img[:, :, 2]
    result = 1 + (r * 10 + g * 100 + b * 1000 + d) % (size - 1)  # noqa
    return result


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
    values, counts = np.unique(indexes, return_counts=True)
    p = w * h
    top = values[counts / p * 100.0 > top_frequency]
    top_size, *_ = top.shape
    result = np.zeros((top_size, 3), dtype="uint8")
    for i, index in enumerate(top):
        result[i, :] = img[indexes == index, :][0]

    return result


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
    mask = None
    for color in colors:
        e = np.full((h, w, 3), color, dtype="int")
        diff = (np.abs(e - values) / 255.0).sum(axis=2) / 3.0
        mask = (diff <= th) if mask is None else mask & (diff <= th)

    if mask is None:
        return 0
    else:
        count = mask.sum()
        img[mask, :] = white
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
