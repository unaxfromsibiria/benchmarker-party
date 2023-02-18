
import numpy as np

from ..base import BaseReplaser
from ..base import Image
from ..base import dt_now
from .replacer import apply


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
                w, h, img, new_r, new_g, new_b, fl, threshold
            )
            self.operation_time += dt_now() - start_time

        self.replaced = replaced
        img_res = img.reshape((h, w, 3), order="F")
        self.result_image = Image.fromarray(img_res, mode="RGB")
