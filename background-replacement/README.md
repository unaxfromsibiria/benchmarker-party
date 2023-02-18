# The background replacing algorithm

Algorithm of the background replacing with most distributed color and dynamic threshold for nearest color value.

There is demo form, launching with cli:

```bash
python -m bg_replacer.run --form on
```

![Demo form](algorithm_demo.gif)

## Implementations

There are few implementations available (the list is going to extend). Launching to make the performance benchmarking:

```bash
python -m bg_replacer.run  --repeat 100 --impl <implementation>
```

Options:

- `numpy` - using numpy and native operations
- `np+py` - using numpy structures and the same algorithm as C implementation does
- `numba` - using numpy structures and the same algorithm under "numba magic"
- `numba+np` - numba using numpy operations and structures
- `cython` - Cython code with adaptation for native C
- `cffi` - only C with binding for Python
- `rust` - the same algorithm in Rust with the C-types and unsafe binding (I will add asap, if you interested a lot see the neighbor directory up)

## Launching a test in containers

Numba does not support Python 3.11 currently, therefore full list of results is available in Python 3.10 environment
(PyPy does not show something interesting to me for the case, but there is also existing command to launch).
Most simple way to use `make` still:

```bash
make in_python310
```

and

```bash
make in_python311
```

## The results that someone gotten

I collected the average milliseconds from stdout after comands above, it possible to do themselves.

| Python ver | Implementation | ms |
|--|:--:|--:|
| 3.10 | numpy | 34.7 |
| 3.10 | np+py | 1016 |
| 3.10 | numba | 32.5 |
| 3.10 | numba+np | 116 |
| 3.10 | cython | 4.2 |
| 3.10 | cffi | 3.3 |
| 3.10 | rust | soon |
| 3.11 | numpy | 36.3 |
| 3.11 | np+py | 804 |
| 3.11 | cython | 4.2 |
| 3.11 | cffi | 3.3 |
