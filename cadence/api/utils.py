from pathlib import Path
import warnings

import scipy.io.wavfile as wav

from cadence.api.track import Track


def read_wav(file_path: str | Path):
    """
    Reads a WAV file and returns the sample rate and audio data.

    Args:
        file_path (str | Path): The path to the WAV file.

    Returns:
        tuple[int, np.ndarray]: A tuple containing the sample rate (int) and audio data (numpy array).
    """
    with warnings.catch_warnings(category=wav.WavFileWarning):
        return wav.read(file_path)


def is_valid_track(track: Track) -> bool:
    """
    Checks if a Track object is valid.
    If all of the track's values are the same as the default values,
    it is considered invalid, otherwise it is valid.

    Args:
        track (Track): The Track object to check.

    Returns:
        bool: True if the track is valid, False otherwise.
    """
    return track != Track()  # Compare with default Track instance
