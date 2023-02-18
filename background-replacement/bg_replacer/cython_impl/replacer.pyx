
from libc.stdlib cimport malloc, free, realloc
import cython
cimport numpy as np


cdef int INDEX_SIZE = 32000


cdef int get_color_hash(
    unsigned char c_r, unsigned char c_g, unsigned char c_b
):
    """Hash function for a color value.
    """
    cdef int r = cython.cast("int", c_r)
    cdef int g = cython.cast("int", c_g)
    cdef int b = cython.cast("int", c_b)
    cdef int m = r + g + b
    return 1 + (r * 10 + g * 100 + b * 1000 + m * m) % (INDEX_SIZE - 1)


cdef struct StatFrequency:
    int size
    unsigned char *colors


cdef StatFrequency search_top_frequency(
    int w,
    int h,
    char *img,
    float top_frequency
):
    """Index with frequency of color for pixel.
    """
    cdef int i = -1
    cdef int index_i, x, top_size = 0
    cdef int delta = w * h
    cdef int *index_values
    cdef unsigned char *stat
    cdef unsigned char r, g, b
    cdef float p = delta / 100.0
    cdef StatFrequency result
    cdef int *index = <int *>malloc(sizeof(int) * INDEX_SIZE)

    for x in range(INDEX_SIZE):
        index[x] = 0

    for _ in range(w):
        for _ in range(h):
            i += 1
            r = img[i]
            g = img[i + delta]
            b = img[i + delta * 2]
            index_i = get_color_hash(r, g, b)
            index[index_i] = index[index_i] + 1

    for i in range(INDEX_SIZE):
        if index[i] / p > top_frequency:
            top_size += 1

    index_values = <int *>malloc(sizeof(int) * top_size)
    stat = <unsigned char *>malloc(sizeof(char) * top_size * 3)
    result.size = top_size
    x = -1

    for i in range(INDEX_SIZE):
        if index[i] / p > top_frequency:
            x += 1
            index_values[x] = i

    i = -1
    for _ in range(w):
        for _ in range(h):
            i += 1
            r = img[i]
            g = img[i + delta]
            b = img[i + delta * 2]
            index_i = get_color_hash(r, g, b)
            if index[index_i] / p * 100.0 > top_frequency:
                for t in range(top_size):
                    if index_values[t] == index_i:
                        stat[t * 3] = r
                        stat[t * 3 + 1] = g
                        stat[t * 3 + 2] = b
                        break

    free(index_values)
    free(index)
    result.colors = stat
    return result


cdef int replace_bg(
    int w,
    int h,
    char *img,
    StatFrequency colors,
    unsigned char new_r,
    unsigned char new_g,
    unsigned char new_b,
    float threshold
):
    """Prepare result array.
    """
    cdef int count = 0
    cdef int i = -1
    cdef int delta = w * h
    cdef float c_s = 255.0
    cdef float a_lim = 0.0
    cdef int r, g, b, r_c, g_c, b_c
    cdef unsigned char buf = 0

    for _ in range(w):
        for _ in range(h):
            i += 1

            buf = img[i]
            r = cython.cast("int", buf)
            buf = img[i + delta]
            g = cython.cast("int", buf)
            buf = img[i + delta * 2]
            b = cython.cast("int", buf)

            for c_i in range(colors.size):
                buf = colors.colors[c_i * 3]
                r_c = cython.cast("int", buf)
                buf = colors.colors[c_i * 3 + 1]
                g_c = cython.cast("int", buf)
                buf = colors.colors[c_i * 3 + 2]
                b_c = cython.cast("int", buf)
                a_lim = (
                    abs(r - r_c) / c_s + abs(g - g_c) / c_s + abs(b - b_c) / c_s
                ) / 3.0
                if threshold >= a_lim:
                    count += 1
                    img[i] = new_r
                    img[i + delta] = new_g
                    img[i + delta * 2] = new_b
                    break

    return int(float(count) / float(delta) * 100.0 + 0.5)


cdef float internal_apply(
    int w,
    int h,
    np.ndarray[char, ndim=1, mode="c"] img,
    int new_r,
    int new_g,
    int new_b,
    float area_frequency_limit,
    float threshold
):
    cdef float result = 0
    cdef StatFrequency colors
    cdef char *img_data = img.data

    if threshold > 0:
        colors = search_top_frequency(
            w, h, img_data, area_frequency_limit
        )
        result = replace_bg(
            w, h, img_data, colors, new_r, new_g, new_b, threshold / 100.0
        )
        free(colors.colors)

    return result


def apply(
    w,
    h,
    np.ndarray[char, ndim=1, mode="c"] img not None,
    new_r,
    new_g,
    new_b,
    area_frequency_limit,
    threshold
):
    return internal_apply(
        w, h, img, new_r, new_g, new_b, area_frequency_limit, threshold
    )
