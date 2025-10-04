from typing import NamedTuple


class Track(NamedTuple):
    """
    Represents a track with audio file information and timing data.

    Attributes:
        name (str): Name of the sound. Defaults to None.
        path (str): File path to .wav file. Defaults to None.
        timing (list[int]): List of timings in 1/12ths of a beat. Defaults to [].
        attack (float): Attack time in seconds. Defaults to 0.0.
        volume (float): Relative volume (0.0 to 1.0). Defaults to 1.0.
    """

    name: str = None
    path: str = None
    timing: list[int] = []
    attack: float = 0.0
    volume: float = 1.0
