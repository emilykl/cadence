import threading

from tkinter import filedialog
from customtkinter import CTkButton

from cadence.api.functions import load_project, play_sound_file
from cadence.ui.state import app_state
from cadence.ui.ui_constants import STYLE
from cadence.ui.utils import update_track_ui_from_tracks, update_tracks_from_track_ui


# Function to handle button clicks
def on_button_click(button: CTkButton):
    """
    Handle button click events to toggle button state and update app_state.

    Args:
        button (CTkButton): The button that was clicked

    Returns: None
    """

    # Toggle button state
    button.enabled = not button.enabled

    # Update app_state
    app_state.update_track_timings()

    # Update button color
    if button.enabled:
        button.configure(fg_color=STYLE["btn_color_selected"])
        button.configure(hover_color=STYLE["btn_color_selected"])
    else:
        if button.is_even:
            button.configure(fg_color=STYLE["btn_color_light"])
            button.configure(hover_color=STYLE["btn_color_light_hover"])
        else:
            button.configure(fg_color=STYLE["btn_color_dark"])
            button.configure(hover_color=STYLE["btn_color_dark_hover"])


def on_play_sound(play_sound_button: CTkButton):
    """Handle play sound button click

    Args:
        play_sound_button (CTkButton): The button that was clicked

    Returns: None
    """
    if not play_sound_button.path:
        return

    def _play_sound():
        play_sound_file(play_sound_button.path)

    threading.Thread(target=_play_sound).start()


def on_play(play_button: CTkButton):
    """
    Handle play button click

    Args:
        play_button (CTkButton)

    Returns: None
    """

    def _play():
        try:
            app_state.play(wait=True)
        finally:
            on_stop(play_button)

    play_button.enabled = True
    play_button.configure(fg_color=STYLE["btn_color_selected"])
    play_button.configure(hover_color=STYLE["btn_color_selected"])
    play_button.configure(text_color=STYLE["btn_color_dark"])
    threading.Thread(target=_play).start()


def on_stop(play_button: CTkButton):
    """
    Handle stop button click

    Args:
        play_button (CTkButton)

    Returns: None
    """
    app_state.stop()
    play_button.enabled = False
    play_button.configure(fg_color=STYLE["btn_color_dark"])
    play_button.configure(hover_color=STYLE["btn_color_dark_hover"])
    play_button.configure(text_color=STYLE["btn_text_color"])


def on_choose_sound(track_index: int, play_sound_button: CTkButton):
    """
    Handle click on "choose sound" button

    Args:
        track_index (int): Index of the track to update
        play_sound_button (CTkButton): The associated "play sound" button
          (We get the current sound path from this button)

    Returns: None
    """
    file_path = filedialog.askopenfilename(
        title=f"Choose sound for track {track_index + 1}",
        filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
        initialfile=play_sound_button.path,
    )
    if not file_path:
        return

    play_sound_button.path = file_path

    # TODO: this function should just update the tracks dirctly
    # instead of returning them; there's a reason I did this (because of the config)
    # but it doesn't have to be this way
    app_state.tracks = update_tracks_from_track_ui(
        app_state.all_play_sound_buttons, app_state.all_name_labels, app_state.tracks
    )

    # if not app_state.tracks:
    #     app_state.tracks = []
    # while track_index >= len(app_state.tracks):
    #     app_state.tracks.append(Track())

    # curr_track = app_state.tracks[track_index]
    # curr_track = curr_track._replace(path=file_path)
    # if not curr_track.name:
    #     curr_track = curr_track._replace(name=DEFAULT_TRACK_LABELS[track_index])
    # app_state.tracks[track_index] = curr_track

    update_track_ui_from_tracks(
        app_state.all_play_sound_buttons,
        app_state.all_name_labels,
        app_state.tracks,
    )


def on_save_project():
    """
    Handle save project button click.

    Opens a file dialog to save the current project to a .cadence file.

    Returns: None
    """
    file_path = filedialog.asksaveasfilename(
        title="Save project",
        defaultextension=".cadence",
        filetypes=[("Cadence project files", "*.cadence"), ("All files", "*.*")],
    )
    if file_path:
        app_state.save_project(file_path)


def on_export_wav():
    """
    Handle export WAV button click.

    Opens a file dialog to export the current project as a WAV audio file.

    Returns: None
    """
    file_path = filedialog.asksaveasfilename(
        title="Export as WAV",
        defaultextension=".wav",
        filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
    )
    if file_path:
        app_state.save_sound(file_path)


def on_load_project(
    all_buttons: dict[tuple[int, int, int, int], CTkButton],
):
    """
    Handle load project button click.

    Opens a file dialog to load a project from a .cadence file and updates the application state.

    Args:
        all_buttons (dict[tuple[int, int, int, int], CTkButton]): Dictionary of all buttons in the UI.

    Returns: None
    """
    file_path = filedialog.askopenfilename(
        title="Load project",
        filetypes=[("Cadence project directories", "*.cadence")],
    )
    if not file_path:
        return

    tracks, config = load_project(file_path)
    app_state.set_config(config)
    app_state.set_tracks(tracks)

    # The below shouldn't be necessary
    # app_state.update_track_timings(all_buttons)
