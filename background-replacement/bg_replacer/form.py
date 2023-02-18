import tkinter as tk

from PIL import ImageTk

from .base import BaseReplaser


def apply(
    replaser: BaseReplaser,
    frequency_limit: float,
    color_threshold: float,
    img_container: tk.Label,
):
    """Create a new image.
    """
    frequency_limit = frequency_limit or 0
    color_threshold = color_threshold or 0
    if 1 <= frequency_limit <= 99 and 1 <= color_threshold <= 99:
        replaser.area_frequency_limit = frequency_limit
        replaser.color_threshold = color_threshold
        replaser.apply(1)
        photo = ImageTk.PhotoImage(replaser.result_image)
        img_container.configure(image=photo)
        img_container.image = photo
        print(
            f"with area frequency limit: {frequency_limit}",
            f"and color threshold: {color_threshold}",
            replaser.time_result()
        )


form_data = {
    "replaser": None,
    "frequency_limit": None,
    "color_threshold": None,
    "img_container": None,
}


def slider_1_move(event):
    form_data.update(frequency_limit=float(event))
    apply(**form_data)


def slider_2_move(event):
    form_data.update(color_threshold=float(event))
    apply(**form_data)


def create(replaser: BaseReplaser):
    win = tk.Tk()
    img = replaser.rgb_image
    w, h = img.size
    win.geometry(f"{w + 8}x{h + 100}")
    win.title(
        f"Class: {replaser.__class__.__module__} image: {replaser.image_path}"
    )

    slider_1 = tk.Scale(
        win, from_=1, to=99, orient=tk.HORIZONTAL, command=slider_1_move
    )
    slider_1.set(replaser.area_frequency_limit)
    slider_1.pack()
    slider_2 = tk.Scale(
        win, from_=1, to=99, orient=tk.HORIZONTAL, command=slider_2_move
    )
    slider_2.set(replaser.color_threshold)
    slider_2.pack()

    photo = ImageTk.PhotoImage(img)
    label = tk.Label(image=photo)
    label.image = photo
    label.pack()
    form_data.update(
        replaser=replaser, img_container=label
    )

    win.mainloop()
