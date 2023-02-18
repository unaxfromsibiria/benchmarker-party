import os
from time import monotonic as dt_now
from typing import Tuple

from PIL import Image


class BaseReplaser:
    new_color: Tuple[int, int, int] = (255, 255, 255)
    area_frequency_limit: float
    color_threshold: float

    operation_time: float = 0
    operation_repeat: float = 100
    image_path: str
    rgb_image: Image
    result_image: Image
    w = h = 0
    replaced: float = 0

    def __init__(
        self,
        image_path: str,
        area_frequency_limit: float = 10,
        color_threshold: float = 25,
    ):
        self.area_frequency_limit = area_frequency_limit
        self.color_threshold = color_threshold
        self.image_path = image_path
        with Image.open(image_path) as img_src:
            self.rgb_image = img = img_src.convert("RGB")

        self.w = img.width
        self.h = img.height

    def apply(self, operation_repeat: int):
        self.operation_repeat = operation_repeat

    def save(self, img_path: str = "") -> bool:
        if not img_path:
            src_file = os.path.basename(self.image_path)
            name, *_ = src_file.rsplit(".", 1)
            img_path = self.image_path.replace(src_file, f"new_bg_{name}.png")

        if self.result_image:
            self.result_image.save(img_path, format="png")
            return True
        else:
            return False

    def time_result(self) -> str:
        t = round(1000 * self.operation_time / self.operation_repeat, 2)
        r = round(self.replaced, 2)
        return (
            f"{self.__class__.__name__}: time {t} ms. Replaced area: {r}"
            f" image {self.w}x{self.h}"
        )
