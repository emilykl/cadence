from customtkinter import CTkButton, CTkEntry

from cadence.api.constants import TIMING_UNITS_PER_BEAT
from cadence.api.track import Track
from cadence.api.config import Config
from cadence.ui.ui_constants import (
    DEFAULT_TRACK_LABELS,
    DIVS_PER_BEAT_UPPER,
    DIVS_PER_BEAT_LOWER,
    STYLE,
    UI_DEFAULT_BPM,
    UI_DEFAULT_REPEATS,
    UI_MAX_BPM,
    UI_MAX_REPEATS,
)


def get_timing_index(division: int, button_index: int) -> int:
    """
    Calculate the timing index based on the division and button index.

    Args:
        division (int): 0 for upper division, 1 for lower division.
        button_index (int): The index of the button within its division.

    Returns:
        int: The calculated timing index.
    """
    if division == 0:
        return button_index * (TIMING_UNITS_PER_BEAT // DIVS_PER_BEAT_UPPER)
    else:  # division == 1
        return button_index * (TIMING_UNITS_PER_BEAT // DIVS_PER_BEAT_LOWER)


def get_button_info(timing: int) -> tuple[int, int, int]:
    """
    Given a timing value, return the corresponding beat, division, and button index.

    Args:
        timing (int): The timing value to convert.

    Returns:
        tuple[int, int, int]: A tuple containing the beat, division, and button index.
    """
    beat = timing // TIMING_UNITS_PER_BEAT
    timing_index = timing % TIMING_UNITS_PER_BEAT

    fits_in_upper = timing_index % (TIMING_UNITS_PER_BEAT // DIVS_PER_BEAT_UPPER) == 0
    fits_in_lower = timing_index % (TIMING_UNITS_PER_BEAT // DIVS_PER_BEAT_LOWER) == 0

    if fits_in_upper and fits_in_lower:
        division = 0  # Prefer upper division if fits in both
        btn_index = timing_index // (TIMING_UNITS_PER_BEAT // DIVS_PER_BEAT_UPPER)
        return beat, division, btn_index
    elif fits_in_upper:
        division = 0
        btn_index = timing_index // (TIMING_UNITS_PER_BEAT // DIVS_PER_BEAT_UPPER)
        return beat, division, btn_index
    else:  # Fits in lower
        assert fits_in_lower, f"Timing {timing} does not fit in either division"
        division = 1
        btn_index = timing_index // (TIMING_UNITS_PER_BEAT // DIVS_PER_BEAT_LOWER)
        return beat, division, btn_index


def update_button_state_from_tracks(
    all_buttons: dict[tuple[int, int, int, int], CTkButton],
    tracks: list[Track],
):
    """
    Update the state of buttons based on the provided tracks.

    Args:
        all_buttons (dict[tuple[int, int, int, int], CTkButton]): Dictionary of buttons to update.
        tracks (list[Track]): List of Track objects defining the sounds and their timings.

    Returns: None
    """
    # First, disable all buttons
    for button in all_buttons.values():
        button.enabled = False
        if button.is_even:
            button.configure(fg_color=STYLE["btn_color_light"])
            button.configure(hover_color=STYLE["btn_color_light_hover"])
        else:
            button.configure(fg_color=STYLE["btn_color_dark"])
            button.configure(hover_color=STYLE["btn_color_dark_hover"])

    # Enable buttons based on tracks
    for i, track in enumerate(tracks):
        for t in track.timing:
            beat, division, btn_index = get_button_info(t)
            btn_to_enable = all_buttons[(i, beat, division, btn_index)]

            btn_to_enable.enabled = True
            if btn_to_enable.is_even:
                btn_to_enable.configure(fg_color=STYLE["btn_color_selected"])
                btn_to_enable.configure(hover_color=STYLE["btn_color_selected"])
            else:
                btn_to_enable.configure(fg_color=STYLE["btn_color_selected"])
                btn_to_enable.configure(hover_color=STYLE["btn_color_selected"])


def update_track_ui_from_tracks(
    all_play_sound_buttons: list[CTkButton],
    all_name_labels: list[CTkEntry],
    tracks: list[Track],
):
    """
    Update the labels of tracks based on the provided tracks.

    Args:
        all_play_sound_buttons (list[CTkButton]): List of play sound buttons to update.
        all_name_labels (list[CTkEntry]): List of name labels to update.
        tracks (list[Track]): List of Track objects defining the sounds and their timings.

    Returns: None
    """
    for i, (play_sound_btn, name_label) in enumerate(
        zip(all_play_sound_buttons, all_name_labels)
    ):
        track = tracks[i] if i < len(tracks) else None

        # Update play sound button
        if track and track.path:
            play_sound_btn.path = track.path
            play_sound_btn.configure(state="normal")
            play_sound_btn.configure(fg_color=STYLE["btn_color_dark"])
            play_sound_btn.configure(hover_color=STYLE["btn_color_dark_hover"])
            play_sound_btn.configure(text="🔊")
        else:
            play_sound_btn.path = None
            play_sound_btn.configure(state="disabled")
            play_sound_btn.configure(fg_color=STYLE["bkg_color"])
            play_sound_btn.configure(text="")

        # Update name label
        if track and track.name:
            name_label.cget("textvariable").set(track.name)
            if track.path:
                name_label.configure(text_color=STYLE["lbl_text_color"])
            else:
                name_label.configure(text_color=STYLE["lbl_text_color_inactive"])
        else:
            # name_label.configure(text=DEFAULT_TRACK_LABELS[i])
            name_label.configure(text_color=STYLE["lbl_text_color_inactive"])

        # Update file label
        if track and track.path:
            play_sound_btn.path = track.path  # Store path in button for reference
            play_sound_btn.configure(state="normal")
            play_sound_btn.configure(fg_color=STYLE["btn_color_dark"])
        else:
            play_sound_btn.path = None
            play_sound_btn.configure(state="disabled")
            play_sound_btn.configure(fg_color=STYLE["bkg_color"])


def update_tracks_from_track_ui(
    all_play_sound_buttons: list[CTkButton],
    all_name_labels: list[CTkEntry],
    tracks: list[Track],
):
    """
    Update the provided tracks based on the current state of the UI elements.

    Args:
        all_play_sound_buttons (list[CTkButton]): List of play sound buttons to read from.
        all_name_labels (list[CTkEntry]): List of name labels to read from.
        tracks (list[Track]): List of Track objects to update.

    Returns:
        list[Track]: Updated list of Track objects.
    """
    new_tracks = []
    for i, (play_sound_btn, name_label) in enumerate(
        zip(all_play_sound_buttons, all_name_labels)
    ):
        if i >= len(tracks):
            existing_track = Track()
        else:
            existing_track = tracks[i]

        # Update track name
        if name_label and name_label.cget("textvariable").get():
            new_name = name_label.get()
        else:
            new_name = DEFAULT_TRACK_LABELS[i]

        # Update track path
        if play_sound_btn and play_sound_btn.path:
            new_path = play_sound_btn.path
        else:
            new_path = None

        # TODO: Update attack and volume from UI if we add those controls

        new_track = Track(
            name=new_name,
            path=new_path,
            timing=existing_track.timing,
            attack=existing_track.attack,
            volume=existing_track.volume,
        )

        new_tracks.append(new_track)
    return new_tracks


def update_config_from_config_ui(
    bpm_entry: CTkEntry,
    repeat_entry: CTkEntry,
    config: Config,
):
    """
    Update the provided config based on the current state of the UI elements.

    Args:
        bpm_entry (CTkEntry): Entry widget for BPM.
        repeat_entry (CTkEntry): Entry widget for repeat count.
        config (Config): Config object to update.

    Returns:
        Config: Updated Config object with values from the UI.
    """
    # Update BPM
    try:
        new_bpm = int(bpm_entry.get())
    except ValueError:
        new_bpm = UI_DEFAULT_BPM
    new_bpm = min(max(0, new_bpm), UI_MAX_BPM)
    # Reflect sanitized value back to UI
    bpm_entry.cget("textvariable").set(str(new_bpm))

    # Update repeat count
    try:
        new_repeat = int(repeat_entry.get())
    except ValueError:
        new_repeat = UI_DEFAULT_REPEATS
    new_repeat = min(max(1, new_repeat), UI_MAX_REPEATS)
    # Reflect sanitized value back to UI
    repeat_entry.cget("textvariable").set(str(new_repeat))

    existing_config = config if config else Config()

    # TODO: Update measures and beats per measure from UI if we add those controls

    return Config(
        bpm=new_bpm,
        beats_per_measure=existing_config.beats_per_measure,
        measures=existing_config.measures,
        repeat=new_repeat,
    )


def update_config_ui_from_config(
    bpm_entry: CTkEntry,
    repeat_entry: CTkEntry,
    config: Config,
):
    """
    Update the UI elements based on the provided config.

    Args:
        bpm_entry (CTkEntry): Entry widget for BPM.
        repeat_entry (CTkEntry): Entry widget for repeat count.
        config (Config): Config object to read values from.

    Returns: None
    """
    config = config or Config()

    # Update BPM
    bpm_entry.cget("textvariable").set(str(config.bpm))

    # Update repeat count
    repeat_entry.cget("textvariable").set(str(config.repeat))
