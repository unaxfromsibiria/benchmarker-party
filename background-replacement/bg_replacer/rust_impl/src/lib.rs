const INDEX_SIZE: usize = 32000;

struct StatFrequency {
    size: usize,
    colors: Vec<u8>,
}

fn get_color_hash(c_r: u8, c_g: u8, c_b: u8) -> usize {
    let r = c_r as i32;
    let g = c_g as i32;
    let b = c_b as i32;
    let m = r + g + b;
    (1 + (r * 10 + g * 100 + b * 1000 + m * m) % (INDEX_SIZE as i32 - 1)) as usize
}

fn search_top_frequency(w: i32, h: i32, img: &[u8], top_frequency: f32) -> StatFrequency {
    let delta: usize = (w * h) as usize;
    let mut index: Vec<i32> = Vec::new();
    index.resize(INDEX_SIZE, 0i32);

    let mut r;
    let mut g;
    let mut b;
    let p = delta as f32 / 100.0;
    let mut result: StatFrequency;
    let mut i = 0;

    for k in 0..w {
        for j in 0..h {
            r = img[i];
            g = img[i + delta];
            b = img[i + delta * 2];
            index[get_color_hash(r, g, b)] += 1;
            i += 1;
        }
    }

    let mut top_size = 0;
    for i in 0..INDEX_SIZE {
        if index[i] as f32 / p > top_frequency {
            top_size += 1;
        }
    }

    let mut index_values: Vec<usize> = Vec::new();
    index_values.resize(top_size, 0);

    let mut x = 0;
    for i in 0..INDEX_SIZE {
        if index[i] as f32 / p > top_frequency {
            index_values[x as usize] = i;
            x += 1;
        }
    }

    let mut stat: Vec<u8> = Vec::new();
    stat.resize(top_size * 3, 0u8);

    i = 0;
    for k in 0..w {
        for j in 0..h {
            r = img[i];
            g = img[i + delta];
            b = img[i + delta * 2];
            let index_i = get_color_hash(r, g, b);
            if index[index_i] as f32 / p * 100.0 > top_frequency {
                for x in 0..top_size {
                    if index_values[x] == index_i {
                        stat[x * 3] = r;
                        stat[x * 3 + 1] = g;
                        stat[x * 3 + 2] = b;
                        break;
                    }
                }
            }
            i += 1;
        }
    }
    StatFrequency {
        size: top_size,
        colors: stat,
    }
}

fn replace_bg(
    w: i32,
    h: i32,
    img: &mut [u8],
    colors: StatFrequency,
    new_r: u8,
    new_g: u8,
    new_b: u8,
    threshold: f32,
) -> i32 {
    let mut count = 0;
    let mut i = 0;
    let delta = (w * h) as usize;
    let c_s = 255.0;
    let a_lim = 0.0;

    for k in 0..w {
        for j in 0..h {
            let r = img[i] as i32;
            let g = img[i + delta] as i32;
            let b = img[i + delta * 2] as i32;

            for c_i in 0..colors.size {
                let r_c = colors.colors[c_i * 3] as i32;
                let g_c = colors.colors[c_i * 3 + 1] as i32;
                let b_c = colors.colors[c_i * 3 + 2] as i32;
                let a_lim = ((r - r_c).abs() as f32 / c_s
                    + (g - g_c).abs() as f32 / c_s
                    + (b - b_c).abs() as f32 / c_s)
                    / 3.0;
                if threshold >= a_lim {
                    count += 1;
                    img[i] = new_r;
                    img[i + delta] = new_g;
                    img[i + delta * 2] = new_b;
                    break;
                }
            }
            i += 1;
        }
    }
    (count as f32 / delta as f32 * 100.0 + 0.5) as i32
}

#[no_mangle]
pub extern "C" fn apply(w: i32, h: i32, img: *mut u8, bg: *const u8, params: *const f32) -> i32 {
    let mut result: i32 = 0;
    let size = (w * h * 3) as usize;

    unsafe {
        let src_params = std::slice::from_raw_parts(params, 2);
        let threshold = src_params[1] / 100.0;
        if threshold > 0.0 {
            let src_bg = std::slice::from_raw_parts(bg, 3);
            let src_img = std::slice::from_raw_parts_mut(img, size);
            let bg_r = src_bg[0];
            let bg_g = src_bg[1];
            let bg_b = src_bg[2];
            let fl = src_params[0];
            let colors = search_top_frequency(w, h, src_img, fl);
            result = replace_bg(w, h, src_img, colors, bg_r, bg_g, bg_b, threshold);
        }
        std::mem::forget(img);
        std::mem::forget(bg);
        std::mem::forget(params);
    }
    result
}
