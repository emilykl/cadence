# Configuration constants
N_TRACKS = 8
N_MEASURES = 4
PLAY_BUTTON_HEIGHT = 30
PLAY_BUTTON_WIDTH = 30
PLAY_SOUND_BUTTON_HEIGHT = 20
PLAY_SOUND_BUTTON_WIDTH = 40
CHOOSE_BUTTON_WIDTH = 60
LABEL_WIDTH = 90
BEATS_PER_MEASURE = 4
DIVS_PER_BEAT_UPPER = 4  # Number of button divisions per beat (top row)
DIVS_PER_BEAT_LOWER = 3  # Number of button divisions per beat (bottom row)
BUTTON_SIZE = 28
BUTTON_PAD_X = 1
BUTTON_PAD_Y = 2
TRIPLET_ROW_HEIGHT_FRAC = 0.35  # Height fraction for triplet row

# UI value config
UI_MAX_BPM = 300
UI_DEFAULT_BPM = 120
UI_MAX_REPEATS = 100
UI_DEFAULT_REPEATS = 4

# Derived constants
N_BEATS = N_MEASURES * BEATS_PER_MEASURE

# Style constants
STYLE = {
    "bkg_color": "#242424",  # Dark grey
    "btn_color_dark": "#2B5A87",  # Dark blue
    "btn_color_light": "#4A9FE7",  # Light blue
    "btn_color_dark_hover": "#1A4A72",  # Dark blue hover
    "btn_color_light_hover": "#2D7BB8",  # Light blue hover
    "btn_color_disabled": "#46596C",  # Darker blue
    "btn_text_color": "#FFFFFF",
    "btn_color_selected": "#FFFFFF",
    "lbl_text_color": "#FFFFFF",
    "lbl_text_color_inactive": "#777777",
    # "track_entry_border_color": "#363636",
    # "track_entry_fill_color": "#303030",
    "track_entry_fill_color": "#242424",
}

# Default labels
DEFAULT_FILE_LABEL = "(no file)"
DEFAULT_TRACK_LABELS = [f"Track {i + 1}" for i in range(N_TRACKS)]
