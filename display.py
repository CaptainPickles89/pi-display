from functools import lru_cache

from inky.auto import auto


@lru_cache(maxsize=1)
def get_display():
    """Return the process-wide Inky display instance, initialising it once.

    auto() opens hardware handles (SPI/GPIO/I2C) that are never closed by the
    inky library, so calling it fresh every cycle leaks file descriptors until
    the process hits its open-file limit. Caching keeps it to a single open.
    """
    return auto()
