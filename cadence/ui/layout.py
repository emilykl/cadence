import functools

from customtkinter import (
    CTkButton,
    CTkEntry,
    CTkFrame,
    CTkLabel,
    CTkScrollableFrame,
    StringVar,
)

from cadence.ui.callbacks import (
    on_button_click,
    on_choose_sound,
    on_play,
    on_play_sound,
    on_stop,
    on_save_project,
    on_export_wav,
    on_load_project,
)
from cadence.ui.state import app_state
from cadence.ui.ui_constants import (
    N_BEATS,
    N_TRACKS,
    PLAY_BUTTON_HEIGHT,
    PLAY_BUTTON_WIDTH,
    PLAY_SOUND_BUTTON_HEIGHT,
    PLAY_SOUND_BUTTON_WIDTH,
    CHOOSE_BUTTON_WIDTH,
    LABEL_WIDTH,
    BUTTON_SIZE,
    TRIPLET_ROW_HEIGHT_FRAC,
    DEFAULT_TRACK_LABELS,
    STYLE,
    DIVS_PER_BEAT_UPPER,
    DIVS_PER_BEAT_LOWER,
    BUTTON_PAD_X,
    BUTTON_PAD_Y,
    UI_DEFAULT_BPM,
    UI_DEFAULT_REPEATS,
)
from cadence.ui.utils import get_timing_index


def add_layout(app):
    """
    Create and add the UI layout to the application window.

    Sets up the main frame, track controls, buttons, and all UI elements.

    Args:
        app (CTk): The main application window.

    Returns: None
    """
    # Configure the main window to center content
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    # Create a main frame to hold everything
    main_frame = CTkFrame(app, fg_color=STYLE["bkg_color"])
    main_frame.grid(row=0, column=0, sticky="", padx=10, pady=10)

    # Add top row of buttons
    play_pause_frame = CTkFrame(main_frame, fg_color=STYLE["bkg_color"])
    play_pause_frame.grid(row=0, column=0, sticky="ew", pady=10)
    play_button = CTkButton(
        play_pause_frame,
        text="▶",
        height=PLAY_BUTTON_HEIGHT,
        width=PLAY_BUTTON_WIDTH,
    )
    play_button.configure(command=functools.partial(on_play, play_button))
    play_button.enabled = False
    play_button.grid(row=0, column=0, padx=10, pady=10)
    stop_button = CTkButton(
        play_pause_frame,
        text="■",
        height=PLAY_BUTTON_HEIGHT,
        width=PLAY_BUTTON_WIDTH,
    )
    stop_button.configure(command=functools.partial(on_stop, play_button))
    stop_button.grid(row=0, column=1, padx=10, pady=10)

    # Add BPM controls
    bpm_label = CTkLabel(play_pause_frame, text="BPM")
    bpm_label.grid(row=0, column=2, padx=(130, 5), pady=10)
    bpm_entry = CTkEntry(
        play_pause_frame,
        width=60,
        fg_color=STYLE["track_entry_fill_color"],
        textvariable=StringVar(value=UI_DEFAULT_BPM),
    )
    bpm_entry.grid(row=0, column=3, pady=10)
    app_state.bpm_entry = bpm_entry

    # Add repeat controls
    repeat_label = CTkLabel(play_pause_frame, text="Repeats")
    repeat_label.grid(row=0, column=4, padx=(10, 5), pady=10)
    repeat_entry = CTkEntry(
        play_pause_frame,
        width=60,
        fg_color=STYLE["track_entry_fill_color"],
        textvariable=StringVar(value=UI_DEFAULT_REPEATS),
    )
    repeat_entry.grid(row=0, column=5, pady=10)
    app_state.repeat_entry = repeat_entry

    # Create a scrollable canvas within the main frame to hold the tracks
    # TODO: fix scrolling; only works when mouse is over scrollbar
    scrollable_area_height = (
        N_TRACKS * (BUTTON_SIZE * (1 + TRIPLET_ROW_HEIGHT_FRAC) + 2 * BUTTON_PAD_Y + 2)
        + 10
    )
    scrollable_tracks_frame = CTkScrollableFrame(
        main_frame,
        height=scrollable_area_height,
        width=1200,
        orientation="horizontal",
        fg_color=STYLE["bkg_color"],
    )
    scrollable_tracks_frame.grid(row=1, column=0, sticky="nsew")

    all_buttons = {}
    all_play_sound_buttons = []
    all_name_labels = []
    # Add 1 row for each track
    for track in range(N_TRACKS):
        # Create frame for entire track row
        track_frame = CTkFrame(scrollable_tracks_frame, fg_color=STYLE["bkg_color"])
        track_frame.grid(row=track, column=0, sticky="ew")

        # Create a frame for the controls on the left, and add to track_frame grid
        controls_frame = CTkFrame(track_frame, fg_color=STYLE["bkg_color"])
        controls_frame.grid(row=0, column=0, sticky="ns")
        controls_frame.grid_rowconfigure(0, weight=1)  # Center vertically

        # Add file controls grid to controls grid
        file_controls_frame = CTkFrame(controls_frame, fg_color=STYLE["bkg_color"])
        file_controls_frame.grid(row=0, column=0, padx=5, sticky="e")

        # Add play sound button to file controls grid
        play_sound_button = CTkButton(
            file_controls_frame,
            text="",
            state="disabled",
            height=PLAY_SOUND_BUTTON_HEIGHT,
            width=PLAY_SOUND_BUTTON_WIDTH,
            fg_color=STYLE["bkg_color"],
        )
        play_sound_button.path = None
        play_sound_button.configure(
            command=functools.partial(on_play_sound, play_sound_button)
        )
        all_play_sound_buttons.append(play_sound_button)
        play_sound_button.grid(row=0, column=0, sticky="e")

        # Add "Choose sound..." button to file controls grid
        choose_button = CTkButton(
            file_controls_frame,
            text="Choose...",
            height=PLAY_SOUND_BUTTON_HEIGHT,
            width=CHOOSE_BUTTON_WIDTH,
            fg_color=STYLE["btn_color_dark"],
            hover_color=STYLE["btn_color_dark_hover"],
            font=("Sans-serif", 10),
            command=functools.partial(on_choose_sound, track, play_sound_button),
        )
        choose_button.grid(row=0, column=1, padx=5, sticky="e")

        # Add track label to controls grid as a CTkEntry so user can edit track name
        label = CTkEntry(
            controls_frame,
            width=LABEL_WIDTH,
            fg_color=STYLE["track_entry_fill_color"],
            textvariable=StringVar(value=DEFAULT_TRACK_LABELS[track]),
        )
        all_name_labels.append(label)
        label.grid(row=0, column=1, sticky="w", padx=5)

        # Create a frame for the buttons on the right, and add to track_frame grid
        buttons_frame = CTkFrame(track_frame, fg_color=STYLE["bkg_color"])
        buttons_frame.grid(row=0, column=1, sticky="ew")
        buttons_frame.grid_columnconfigure(0, weight=1)  # Expand to fill space

        # Determine button color based on track index (alternating colors)
        if track % 2 == 0:
            button_color = STYLE["btn_color_light"]
            button_color_hover = STYLE["btn_color_light_hover"]
            is_even = True
        else:
            button_color = STYLE["btn_color_dark"]
            button_color_hover = STYLE["btn_color_dark_hover"]
            is_even = False

        # Loop through each beat
        for beat in range(N_BEATS):
            # Create a beat frame for this beat's buttons
            beat_frame = CTkFrame(buttons_frame, fg_color=STYLE["bkg_color"])
            beat_frame.grid(row=0, column=beat)

            # Add buttons to upper division
            # Create frame for upper division buttons
            upper_div_frame = CTkFrame(beat_frame, fg_color=STYLE["bkg_color"])
            upper_div_frame.grid(row=0, column=0)
            for i in range(DIVS_PER_BEAT_UPPER):
                button = CTkButton(
                    upper_div_frame,
                    text="",
                    width=BUTTON_SIZE,
                    height=BUTTON_SIZE,
                    fg_color=button_color,
                    hover_color=button_color_hover,
                )
                button.configure(command=functools.partial(on_button_click, button))
                button.enabled = False
                button.is_even = is_even
                button.track = track
                button.beat = beat
                button.division = 0
                button.button_index = i
                button.timing_index = get_timing_index(0, i)
                button.grid(row=0, column=i, padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y)

                all_buttons[
                    (button.track, button.beat, button.division, button.button_index)
                ] = button

            # Add buttons to lower division
            # First, calculate button width to align with upper division
            # bottom_button_width = ((BUTTON_SIZE+per_button_padding_top)*N_BUTTONS_TOP)/N_BUTTONS_BOTTOM - per_button_padding_bottom
            pad = BUTTON_PAD_X * 2
            bottom_button_width = (
                (BUTTON_SIZE + pad) * DIVS_PER_BEAT_UPPER
            ) / DIVS_PER_BEAT_LOWER - pad
            # Create frame for lower division buttons
            lower_div_frame = CTkFrame(beat_frame, fg_color=STYLE["bkg_color"])
            lower_div_frame.grid(row=1, column=0)
            for i in range(DIVS_PER_BEAT_LOWER):
                button = CTkButton(
                    lower_div_frame,
                    text="",
                    width=bottom_button_width,
                    height=int(BUTTON_SIZE * TRIPLET_ROW_HEIGHT_FRAC),
                    fg_color=button_color,
                    hover_color=button_color_hover,
                )
                button.configure(command=functools.partial(on_button_click, button))
                button.enabled = False
                button.is_even = is_even
                button.track = track
                button.beat = beat
                button.division = 1
                button.button_index = i
                button.timing_index = get_timing_index(1, i)
                button.grid(row=1, column=i, padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y)

                all_buttons[
                    (button.track, button.beat, button.division, button.button_index)
                ] = button

    app_state.all_buttons = all_buttons
    app_state.all_play_sound_buttons = all_play_sound_buttons
    app_state.all_name_labels = all_name_labels

    # Add save/load buttons row
    save_load_frame = CTkFrame(main_frame, fg_color=STYLE["bkg_color"])
    save_load_frame.grid(row=N_TRACKS, column=0, sticky="ew", pady=10)

    # Save project button
    save_project_button = CTkButton(
        save_load_frame,
        text="Save project...",
        height=30,
        width=120,
        fg_color=STYLE["btn_color_dark"],
        hover_color=STYLE["btn_color_dark_hover"],
        command=lambda: on_save_project(),
    )
    save_project_button.grid(row=0, column=0, padx=10, pady=10)

    # Export WAV button
    export_wav_button = CTkButton(
        save_load_frame,
        text="Export .wav...",
        height=30,
        width=120,
        fg_color=STYLE["btn_color_dark"],
        hover_color=STYLE["btn_color_dark_hover"],
        command=on_export_wav,
    )
    export_wav_button.grid(row=0, column=1, padx=10, pady=10)

    # Load project button
    load_project_button = CTkButton(
        save_load_frame,
        text="Load project...",
        height=30,
        width=120,
        fg_color=STYLE["btn_color_dark"],
        hover_color=STYLE["btn_color_dark_hover"],
        command=lambda: on_load_project(all_buttons),
    )
    load_project_button.grid(row=0, column=2, padx=50, pady=10)
