from distutils.core import setup
import numpy
from distutils.extension import Extension

from Cython.Build import cythonize

# cd ./bg_replacer/cython_impl/ && python setup.py build_ext --inplace && cd ../../

modules = [
    Extension(
        "replacer",
        ["replacer.pyx"],
        extra_compile_args=[
            "-Ofast",
            "-ffast-math",
            "-march=native",
            "-fopenmp",
            "-ftree-loop-distribution",
            "-floop-nest-optimize",
            "-floop-block",
            "-ftree-vectorize",
        ],
        include_dirs=[numpy.get_include()],
        language="c",
        extra_link_args=["-fopenmp"],
    )
]

setup(
    ext_modules=cythonize(
        modules,
        compiler_directives={
            "initializedcheck": False,
            "nonecheck": False,
            "language_level": 3,
            "infer_types": True,
            "boundscheck": False,
            "cdivision": True,
        }
    )
)
