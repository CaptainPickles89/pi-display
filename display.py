import os
from functools import lru_cache


class _PreviewDisplay:
    """Saves the image to /tmp/inky_preview.png instead of pushing to hardware.
    Set INKY_PREVIEW=1 to use when main.py holds the GPIO pins.
    """
    resolution = (600, 448)

    def set_image(self, image):
        self._image = image

    def show(self):
        path = "/tmp/inky_preview.png"
        self._image.save(path)
        print(f"Preview saved to {path}")


@lru_cache(maxsize=1)
def get_display():
    """Return the process-wide Inky display instance, initialising it once.

    auto() opens hardware handles (SPI/GPIO/I2C) that are never closed by the
    inky library, so calling it fresh every cycle leaks file descriptors until
    the process hits its open-file limit. Caching keeps it to a single open.
    """
    if os.environ.get("INKY_PREVIEW"):
        return _PreviewDisplay()
    from inky.auto import auto
    return auto()
