#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import time

from PIL import Image
from inky.auto import auto


def run_clear(cycles=3):
    inky_display = auto()
    colours = (inky_display.RED, inky_display.BLACK, inky_display.WHITE)
    colour_names = (inky_display.colour, "black", "white")

    img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))

    for i in range(cycles):
        print("Cleaning cycle %i\n" % (i + 1))
        for j, c in enumerate(colours):
            print("- updating with %s" % colour_names[j])
            inky_display.set_border(c)
            for x in range(inky_display.WIDTH):
                for y in range(inky_display.HEIGHT):
                    img.putpixel((x, y), c)
            inky_display.set_image(img)
            inky_display.show()
            time.sleep(1)
        print("\n")

    print("Cleaning complete!")


if __name__ == "__main__":
    print(
        """Inky pHAT: Clean

Displays solid blocks of red, black, and white to clean the Inky pHAT
display of any ghosting.

"""
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--number", "-n", type=int, required=False, help="number of cycles")
    args, _ = parser.parse_known_args()
    run_clear(cycles=args.number if args.number else 3)
