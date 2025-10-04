from typing import NamedTuple


class Config(NamedTuple):
    """
    Config options for a sequence.

    Attributes:
        bpm (int): Tempo in beats per minute. Defaults to 120.
        beats_per_measure (int): Number of beats per measure. Defaults to 4.
        measures (int): Total number of measures. Defaults to None.
        repeat (int): Number of times to repeat the sequence. Defaults to 1.
    """

    bpm: int = 120
    beats_per_measure: int = 4
    measures: int = None
    repeat: int = 1
