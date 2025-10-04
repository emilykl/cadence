from cadence import Track, Config, play

TIMING_SCALE_FACTOR = 3


seq1 = [
    Track(
        name="kick",
        path="sounds/kick1.wav",
        timing=[0, 12, 30, 36],
    ),
    Track(
        name="snare",
        path="sounds/snare.wav",
        timing=[12, 18, 36],
    ),
    Track(
        name="hihat",
        path="sounds/hihat_closed.wav",
        timing=[0, 6, 12, 18, 24, 30, 36, 42],
    ),
]
seq1_config = Config(bpm=120, repeat=4)

play(seq1, seq1_config)
