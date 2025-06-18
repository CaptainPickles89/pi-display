#!/usr/bin/env python3

import sys
import warnings

from PIL import Image

from inky.auto import auto


def display_image(image_path):
    inky = auto()
    image = Image.open(image_path)
    saturation = 0.5
    resizedimage = image.resize(inky.resolution)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Busy Wait: Held high")
        try:
            inky.set_image(resizedimage, saturation=saturation)
        except TypeError:
            inky.set_image(resizedimage)

    inky.show()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]  # Get the image path from the command-line argument
        display_image(image_path)
    else:
        print("No image path provided!")
