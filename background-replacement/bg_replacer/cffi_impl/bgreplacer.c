#include <stdlib.h>
#include <math.h>
#include <stdio.h>

#define INDEX_SIZE 32000

typedef struct StatFrequency
{
    int size;
    unsigned char *colors;
} StatFrequency;

// Hash function for a color value.
int get_color_hash(unsigned char c_r, unsigned char c_g, unsigned char c_b)
{
    int r = (int)c_r;
    int g = (int)c_g;
    int b = (int)c_b;
    int m = r + g + b;
    return 1 + (r * 10 + g * 100 + b * 1000 + m * m) % (INDEX_SIZE - 1);
}

// Index with frequency of color for pixel.
StatFrequency search_top_frequency(int w, int h, char *img, float top_frequency)
{
    int i = -1;
    int index_i, x, k, j;
    int top_size = 0;
    int delta = w * h;
    int *index_values;
    int *index = malloc(sizeof(int) * INDEX_SIZE);
    unsigned char *stat;
    unsigned char r, g, b;
    double p = delta / 100.0;
    StatFrequency result;

    for (j = 0; j < INDEX_SIZE; j++) {
        index[j] = 0;
    }

    for (k = 0; k < w; k++)
    {
        for (j = 0; j < h; j++)
        {
            i++;
            r = (unsigned char)img[i];
            g = (unsigned char)img[i + delta];
            b = (unsigned char)img[i + delta * 2];
            index_i = get_color_hash(r, g, b);
            index[index_i]++;
        }
    }

    for (i = 0; i < INDEX_SIZE; i++)
    {
        if (index[i] / p > top_frequency)
        {
            top_size++;
        }
    }

    stat = malloc(sizeof(char) * top_size * 3);
    result.size = top_size;
    index_values = malloc(sizeof(int) * top_size);
    x = -1;

    for (i = 0; i < INDEX_SIZE; i++)
    {
        if (index[i] / p > top_frequency)
        {
            x++;
            index_values[x] = i;
        }
    }

    i = -1;
    for (k = 0; k < w; k++)
    {
        for (j = 0; j < h; j++)
        {
            i++;
            r = (unsigned char)img[i];
            g = (unsigned char)img[i + delta];
            b = (unsigned char)img[i + delta * 2];
            index_i = get_color_hash(r, g, b);
            if ((double)index[index_i] / p * 100.0 > top_frequency)
            {
                for (x = 0; x < top_size; x++)
                {
                    if (index_values[x] == index_i)
                    {
                        stat[x * 3] = r;
                        stat[x * 3 + 1] = g;
                        stat[x * 3 + 2] = b;
                        break;
                    }
                }
            }
        }
    }

    free(index_values);
    free(index);
    result.colors = stat;
    return result;
}

// Prepare result array.
int replace_bg(
    int w,
    int h,
    char *img,
    StatFrequency colors,
    char new_r,
    char new_g,
    char new_b,
    double threshold
) {
    int count = 0;
    int i = -1;
    int delta = w * h;
    double c_s = 255.0;
    double a_lim = 0.0;
    int j, k, r, c_i, g, b, r_c, g_c, b_c;

    for (k = 0; k < w; k++)
    {
        for (j = 0; j < h; j++)
        {
            i++;
            r = (int)((unsigned char)img[i]);
            g = (int)((unsigned char)img[i + delta]);
            b = (int)((unsigned char)img[i + delta * 2]);

            for (c_i = 0; c_i < colors.size; c_i++)
            {
                r_c = (int)((unsigned char)colors.colors[c_i * 3]);
                g_c = (int)((unsigned char)colors.colors[c_i * 3 + 1]);
                b_c = (int)((unsigned char)colors.colors[c_i * 3 + 2]);
                a_lim = (
                    abs(r - r_c) / c_s + abs(g - g_c) / c_s + abs(b - b_c) / c_s
                ) / 3.0;
                if (threshold >= a_lim)
                {
                    count++;
                    img[i] = new_r;
                    img[i + delta] = new_g;
                    img[i + delta * 2] = new_b;
                    break;
                }
            }
        }
    }

    return (int)((double)count / (double)delta * 100 + 0.5);
}

//
int apply(int w, int h, char *img, char *bg, double fl, double threshold)
{
    int result = -1;
    StatFrequency colors;

    if (threshold > 0) {
        colors = search_top_frequency(w, h, img, fl);
        result = replace_bg(w, h, img, colors, bg[0], bg[1], bg[2], threshold / 100.0);
        free(colors.colors);
    }
    return result;
}
