

# python setup.py
from cffi import FFI

ffibuilder = FFI()

ffibuilder.cdef(
    "int apply(int w, int h, char *img, char *bg, double fl, double threshold);"  # noqa
)

ffibuilder.set_source(
    "replacer",
    """#include "bgreplacer.h" """,
    sources=["bgreplacer.c"],
    extra_compile_args=[
        "-Ofast",
        "-ffast-math",
        "-march=native",
        "-fopenmp",
        "-ftree-loop-distribution",
        "-floop-nest-optimize",
        "-floop-block",
        "-ftree-vectorize",
        # "-pthread",
        # "-lpthread",
    ]
)

ffibuilder.compile(verbose=True)
