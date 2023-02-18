import cffi
from typing import Callable
import os
import numpy as np

from ..base import BaseReplaser
from ..base import Image
from ..base import dt_now

from .replacer import lib


c_apply: Callable = lib.apply


class Replaser(BaseReplaser):
    ffi = cffi.FFI()

    def apply(self, operation_repeat: int):
        self.operation_repeat = operation_repeat
        data = np.asarray(self.rgb_image.convert("RGB"))
        h, w, color = data.shape
        self.w = w
        self.h = h
        src = data.reshape((w * h * color,), order="F").astype("uint8")
        replaced = 0
        fl = self.area_frequency_limit
        threshold = self.color_threshold
        self.operation_time = 0
        ffi = self.ffi

        bg_c_ptr = ffi.cast("char *", ffi.from_buffer(
            np.array(self.new_color).astype("uint8")
        ))

        for _ in range(operation_repeat):
            img = src.copy()
            start_time = dt_now()
            img_c_ptr = ffi.cast("char *", ffi.from_buffer(img))
            replaced = c_apply(w, h, img_c_ptr, bg_c_ptr, fl, threshold)
            self.operation_time += dt_now() - start_time

        self.replaced = float(replaced)
        img_res = img.reshape((h, w, 3), order="F")
        self.result_image = Image.fromarray(img_res, mode="RGB")
