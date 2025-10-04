# Class to capture current state of UI in terms of what should be played

from collections import defaultdict
from pathlib import Path

from customtkinter import CTkButton, CTkEntry

from cadence.api.track import Track
from cadence.api.config import Config
from cadence.api.functions import play, save_project, stop, save_sound
from cadence.ui.utils import (
    update_button_state_from_tracks,
    update_config_from_config_ui,
    update_config_ui_from_config,
    update_tracks_from_track_ui,
    update_track_ui_from_tracks,
)
from cadence.api.constants import TIMING_UNITS_PER_BEAT


class State:
    def __init__(
        self,
        tracks: list[Track] = None,
        config: Config = Config(),
    ):
        self.tracks: list[Track] = tracks or []
        self.config: Config = config

        # UI elements to be set later
        self.all_buttons: dict[tuple[int, int, int], CTkButton] = {}
        self.all_play_sound_buttons: list[CTkButton] = []
        self.all_name_labels: list[CTkEntry] = []
        self.bpm_entry: CTkEntry = None
        self.repeat_entry: CTkEntry = None

    def set_tracks(self, tracks: list[Track]):
        """
        Sets State.tracks to the provided tracks.
        Track timings may be empty lists; they can be updated later
        with the update_tracks() method.

        Args:
            tracks (list[Track]): A list of Track objects to initialize the state with.

        Returns: None
        """
        self.tracks = tracks
        update_button_state_from_tracks(self.all_buttons, self.tracks)
        update_track_ui_from_tracks(
            self.all_play_sound_buttons, self.all_name_labels, self.tracks
        )

    def set_config(self, config: Config):
        """
        Sets State.config to the provided config.

        Args:
            config (Config): A Config object to initialize the state with.

        Returns: None
        """
        self.config = config
        update_config_ui_from_config(self.bpm_entry, self.repeat_entry, self.config)

    def update_track_timings(self):
        """
        Updates State.tracks with the correct data based on the current state of the buttons.

        Returns: None
        """
        timings = defaultdict(list)

        for btn in self.all_buttons.values():
            if btn.enabled:
                timings[btn.track].append(
                    btn.beat * TIMING_UNITS_PER_BEAT + btn.timing_index
                )

        new_n_tracks = max(timings.keys()) + 1 if timings else 0
        existing_n_tracks = len(self.tracks)

        for track_index in range(max(new_n_tracks, existing_n_tracks)):
            if track_index >= len(self.tracks):
                existing_track = Track()
            else:
                existing_track = self.tracks[track_index]
            new_track = Track(
                name=existing_track.name,
                path=existing_track.path,
                timing=sorted(timings[track_index]),
                attack=existing_track.attack,
                volume=existing_track.volume,
            )
            if track_index >= len(self.tracks):
                self.tracks.append(new_track)
            else:
                self.tracks[track_index] = new_track

    def stop(self):
        """
        Stops any currently playing sound.
        """
        stop()

    def play(self, wait: bool = False):
        """
        Plays the current state of the tracks.

        Args:
            wait (bool): If True, block until playback is finished.
                (default: False)

        Returns: None
        """
        self.stop()
        self.config = update_config_from_config_ui(
            self.bpm_entry, self.repeat_entry, self.config
        )
        play(self.tracks, self.config, wait=wait)

    def save_sound(self, file_path: Path):
        """
        Saves the current state of the tracks to a WAV file.

        Args:
            file_path (Path): The path to the WAV file to save.

        Returns: None
        """
        self.tracks = update_tracks_from_track_ui(
            self.all_play_sound_buttons, self.all_name_labels, self.tracks
        )
        self.config = update_config_from_config_ui(
            self.bpm_entry, self.repeat_entry, self.config
        )
        save_sound(file_path, self.tracks, self.config)

    def save_project(self, file_path: Path):
        """
        Saves the current state of the tracks and config to a folder containing
        a JSON file and all individual sound files.

        Args:
            file_path (Path): The path to the folder to save.

        Returns: None
        """
        self.tracks = update_tracks_from_track_ui(
            self.all_play_sound_buttons, self.all_name_labels, self.tracks
        )
        self.config = update_config_from_config_ui(
            self.bpm_entry, self.repeat_entry, self.config
        )
        save_project(file_path, self.tracks, self.config)


app_state = State()  # Initialize the application state
