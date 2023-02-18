import click

try:
    from .cffi_impl import Replaser as CFFIReplaser
except ImportError:
    CFFIReplaser = None
try:
    from .cython_impl import Replaser as CReplaser
except ImportError:
    CReplaser = None
from .form import create as create_ui
from .np_native import Replaser as NpNativeReplaser
from .np_py import Replaser as NpPyReplaser

try:
    from .numba import Replaser as NmReplaser
    from .numba_np import Replaser as NmNpReplaser
except ImportError:
    NmReplaser = NmNpReplaser = None


names = {
    "numpy": NpNativeReplaser,
    "np+py": NpPyReplaser,
    "numba": NmReplaser,
    "numba+np": NmNpReplaser,
    "cython": CReplaser,
    "cffi": CFFIReplaser,
}


@click.command()
@click.option(
    "--img", default="data/house-1.png", help="Input image"
)
@click.option(
    "--repeat", default=10, help="Repeat operation count"
)
@click.option(
    "--impl", default="numpy", help="Implementation"
)
@click.option(
    "--form", default="", help="Show the UI example with sliders"
)
def run(img: str, repeat: int, impl: str, form: str):

    cls = names[impl]
    replaser = cls(image_path=img)

    if form:
        create_ui(replaser)
    else:
        replaser.apply(repeat)
        replaser.save()
        print(replaser.time_result())


run()
