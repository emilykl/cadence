import json
from math import ceil
from pathlib import Path

import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np

from cadence.api.constants import (
    TIMING_UNITS_PER_BEAT,
    MASTER_VOLUME,
)
from cadence.api.config import Config
from cadence.api.track import Track
from cadence.api.utils import is_valid_track, read_wav


def sequence(
    tracks: list[Track], config: Config | dict = Config()
) -> tuple[np.ndarray, int]:
    """
    Create a full audio sequence from a list of Tracks.

    Args:
        tracks (list[Track]): List of Track objects defining the sounds and their timings
        config (Config or dict): Configuration options for the sequence

    Returns:
        np.ndarray: The full audio sequence as a NumPy array
        int: The sample rate of the audio
    """
    # Filter out tracks with no path
    filtered_tracks = [track for track in tracks if track.path is not None]

    if not filtered_tracks:
        return np.array([]), 44100  # Default sample rate

    if isinstance(config, dict):
        config = Config(**config)

    # Load sound data for each track
    sample_rates, sounds = zip(*[read_wav(track.path) for track in filtered_tracks])

    # Validate sample rates and number of channels
    assert len(set(sample_rates)) == 1, f"Sample rate mismatch: {set(sample_rates)}"
    sample_rate = sample_rates[0]
    assert sample_rate is not None, "Sample rate could not be determined"
    n_channels = 0

    # TODO: below logic is busted; it throws an error at the elif
    # if some sounds are mono and some are stereo
    if set([sound.ndim for sound in sounds]) == {1}:
        n_channels = 1
    elif len(set([sound.shape[1] for sound in sounds])) == 1:
        n_channels = sounds[0].shape[1]
    else:
        raise ValueError(
            f"Sounds have different numbers of channels: {[sound.shape for sound in sounds]}"
        )

    # Determine the length (in number of beats) of the timing pattern by
    # looking at the maximum timing value in the tracks, then rounding up to nearest measure
    # TODO: make pattern length configurable (to allow a silence at the end of a pattern)
    max_timing = max(
        [max(track.timing) if track.timing else 0 for track in filtered_tracks]
    )
    pattern_length_beats = (
        ceil((max_timing + 1) / (TIMING_UNITS_PER_BEAT * config.beats_per_measure))
        * config.beats_per_measure
    )

    # Calculate the number of samples per timing unit and per beat
    samples_per_beat = int((60 / config.bpm) * sample_rate)  # integer
    samples_per_timing_unit = (
        samples_per_beat / TIMING_UNITS_PER_BEAT
    )  # float: very important!

    # Create the initial blank sequence (for a single repeat)
    pattern = np.zeros(
        (pattern_length_beats * samples_per_beat, n_channels), dtype=np.float32
    )

    # Add each track to pattern
    for _, (track, sound) in enumerate(zip(tracks, sounds)):
        attack_samples = int(track.attack * sample_rate)

        for t in track.timing:
            start = int(t * samples_per_timing_unit) - attack_samples
            end = start + len(sound)

            # Check how much to clip from each end (if any)
            # to ensure sound is within bounds of pattern
            clip_from_start = max(0, -start)
            clip_from_end = max(0, end - len(pattern))

            # Add sound into pattern
            scaled_sound = sound * track.volume
            pattern[start + clip_from_start : end - clip_from_end] += scaled_sound[
                clip_from_start : len(sound) - clip_from_end
            ]

    # Normalize amplitude
    max_amplitude = np.max(np.abs(pattern))
    if max_amplitude != 0:
        normalized_pattern = (pattern / max_amplitude) * MASTER_VOLUME
    else:
        normalized_pattern = pattern

    # Repeat the pattern the specified number of times to get the full sequence
    sequence = np.tile(normalized_pattern, (config.repeat, 1))

    return sequence, sample_rate


def play(
    tracks: list[Track],
    config: Config | dict = Config(),
    wait: bool = True,
):
    """
    Play a list of Tracks as an audio file.

    Args:
        tracks (list[Track]): List of Track objects defining the sounds and their timings
        config (Config or dict): Configuration options for playback
        wait (bool): If True, block until playback is finished. Defaults to True.

    Returns: None
    """
    audio_data, sample_rate = sequence(tracks, config=config)

    sd.play(audio_data, sample_rate)
    if wait:
        sd.wait()  # Wait until sound has finished playing
    return


def play_sound_file(
    file_path: str | Path,
    wait: bool = True,
):
    """
    Play a WAV sound file.

    Args:
        file_path (str or Path): The path to the WAV file to play.
        wait (bool): If True, block until playback is finished.
            (default: True)

    Returns: None
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    assert file_path.suffix == ".wav", "File must be a WAV file"
    sample_rate, audio_data = wav.read(file_path)

    # Normalize to a max of 1.0
    max_amplitude = np.max(np.abs(audio_data))
    if max_amplitude != 0:
        audio_data = (audio_data / max_amplitude) * MASTER_VOLUME

    sd.play(audio_data, sample_rate)
    if wait:
        sd.wait()  # Wait until sound has finished playing
    return


def stop():
    """
    Stop any currently playing sound.

    Returns: None
    """
    sd.stop()


def project_to_dict(tracks: list[Track], config: Config | dict = Config()) -> dict:
    """
    Convert a list of Track objects and a Config object to a dictionary.

    Args:
        tracks (list[Track]): List of Track objects to convert.
        config (Config or dict): Configuration options for the project.

    Returns:
        dict: Dictionary representation of the project.
    """
    config = config if isinstance(config, Config) else Config(**config)
    return {
        "tracks": [track._asdict() for track in tracks if is_valid_track(track)],
        "config": config._asdict(),
    }


def dict_to_project(data: dict) -> tuple[list[Track], Config]:
    """
    Convert a dictionary representation of a project to a list of Track objects and a Config object.

    Args:
        data (dict): Dictionary representation of the project.

    Returns:
        tuple[list[Track], Config]: A tuple containing a list of Track objects and a Config object.
    """
    tracks = [Track(**track_data) for track_data in data.get("tracks", [])]
    filtered_tracks = [track for track in tracks if is_valid_track(track)]
    config_data = data.get("config", {})
    config = Config(**config_data) if isinstance(config_data, dict) else Config()
    return filtered_tracks, config


def save_project(
    save_path: str | Path,
    tracks: list[Track],
    config: Config | dict = Config(),
):
    """
    Saves the current state of the project to a .cadence file.
    PROJ_NAME.cadence is actually a directory with the following structure:
    PROJ_NAME.cadence/
        project.json  # JSON file with project data (tracks, config, etc)
        sounds/
            sound1.wav  # WAV files for each sound used in the project

    Args:
        save_path (str or Path): The path to the .cadence file to save.
        tracks (list[Track]): List of Track objects defining the sounds and their timings
        config (Config or dict): Configuration options for the project

    Returns: None
    """
    if isinstance(save_path, str):
        save_path = Path(save_path)

    assert save_path.suffix == ".cadence", "Project path must end with .cadence"
    assert not save_path.exists(), f"Project already exists at {save_path}"

    # Create project directory
    save_path.mkdir(parents=True, exist_ok=False)

    # Create sounds directory
    sounds_path = save_path / "sounds"
    sounds_path.mkdir(parents=True, exist_ok=False)

    # Copy sound files to sounds directory (keep original filenames)
    for track in tracks:
        if not track.path:
            continue
        track_filename = Path(track.path).name
        track_sound_dest = sounds_path / track_filename
        track_sound_dest.write_bytes(Path(track.path).read_bytes())

    # Save project data to project.json
    project_data = project_to_dict(tracks, config)

    # Update track paths to point to sounds/ directory
    for track in project_data["tracks"]:
        if not track["path"]:
            continue
        track_sound_path = Path(track["path"]).name
        track["path"] = str(Path("sounds") / track_sound_path)
    # Write to project.json
    with open(save_path / "project.json", "w") as f:
        json.dump(project_data, f, indent=4)


def load_project(load_path: str | Path) -> tuple[list[Track], Config]:
    """
    Loads a project from a .cadence file.

    Args:
        load_path (str or Path): The path to the .cadence file to load.

    Returns:
        tuple[list[Track], Config]: A tuple containing a list of Track objects and a Config object.
    """
    if isinstance(load_path, str):
        load_path = Path(load_path)

    assert load_path.suffix == ".cadence", "Project path must end with .cadence"
    assert load_path.exists(), f"Project does not exist at {load_path}"
    assert load_path.is_dir(), "Project path must be a directory"

    # Load project data from project.json
    with open(load_path / "project.json", "r") as f:
        project_data = json.load(f)

    # Update track paths to be absolute paths
    for track in project_data["tracks"]:
        if not track["path"]:
            continue
        track_sound_path = Path(track["path"]).name
        track["path"] = str(load_path.absolute() / "sounds" / track_sound_path)

    tracks, config = dict_to_project(project_data)
    return tracks, config


def save_sound(
    file_path: str | Path,
    tracks: list[Track],
    config: Config | dict = Config(),
):
    """
    Sequences the given tracks using the given config, and saves it as a WAV file.

    Args:
        file_path (str or Path): The path to the WAV file to save.
        tracks (list[Track]): List of Track objects defining the sounds and their timings
        config (Config or dict): Configuration options for playback

    Returns: None
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    assert file_path.suffix == ".wav", "File must be a WAV file"
    sound_data, sample_rate = sequence(tracks, config)

    wav.write(file_path, sample_rate, sound_data)
