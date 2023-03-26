import ctypes
from typing import Any
from typing import Optional

import numpy as np

from ..base import BaseReplaser
from ..base import Image
from ..base import dt_now


class Replaser(BaseReplaser):
    """Binding for the rust implementation.
    """

    lib: Optional[Any] = None

    def apply(self, operation_repeat: int):
        self.operation_repeat = operation_repeat
        data = np.asarray(self.rgb_image.convert("RGB"))
        h, w, color = data.shape
        self.w = w
        self.h = h
        src = data.reshape((w * h * color,), order="F").astype("uint8")
        replaced = 0
        self.operation_time = 0

        if self.lib is None:
            self.lib = lib = ctypes.cdll.LoadLibrary(
                "./bg_replacer/rust_impl/target/release/librust_impl.so"
            )
            lib.apply.restype = ctypes.c_int32
        else:
            lib = self.lib

        new_cl = np.array(self.new_color).astype("uint8")
        params = np.array(
            [self.area_frequency_limit, self.color_threshold]
        ).astype("float32")

        for _ in range(operation_repeat):
            img = src.copy()
            start_time = dt_now()
            replaced = lib.apply(
                w,
                h,
                np.ctypeslib.as_ctypes(img),
                np.ctypeslib.as_ctypes(new_cl),
                np.ctypeslib.as_ctypes(params)
            )
            self.operation_time += dt_now() - start_time

        self.replaced = float(replaced)
        img_res = img.reshape((h, w, 3), order="F")
        self.result_image = Image.fromarray(img_res, mode="RGB")
