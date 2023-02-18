
import numpy as np

from cython_impl.field_state import FieldState

from base_areal import BaseAreal


class Areal(BaseAreal):
    """Steps driven by Cython.
    """

    field_state: FieldState

    def init_field(self, size: int):
        self.field_state = FieldState(size)

    def add_point(self, x: int, y: int):
        self.field_state.add_point(x, y)

    def run_step(self):
        self.field_state.evolut()

    def as_state_img(self) -> np.array:
        return self.field_state.as_array() == 0
