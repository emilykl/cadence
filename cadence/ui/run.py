# =====
# From https://github.com/astral-sh/uv/issues/7036
from os import environ
from pathlib import Path
from sys import base_prefix

environ["TCL_LIBRARY"] = str(Path(base_prefix) / "lib" / "tcl8.6")
environ["TK_LIBRARY"] = str(Path(base_prefix) / "lib" / "tk8.6")
# =====

import customtkinter

from cadence.api.functions import load_project
from cadence.ui.layout import add_layout
from cadence.ui.state import app_state


def create_app(project_path: Path = None) -> customtkinter.CTk:
    """
    Create and configure the main application window.

    Args:
        project_path (Path, optional): Path to a .cadence project file to load. Defaults to None.

    Returns:
        (customtkinter.CTk): The configured application window.
    """

    # Create a customtkinter window
    app = customtkinter.CTk()
    app.title("Cadence")

    # Create layout
    add_layout(app)

    # Load project if provided
    if project_path:
        tracks, config = load_project(project_path)

        app_state.set_config(config)
        app_state.set_tracks(tracks)

    return app


def run(project_path: Path = None):
    """
    Run the Cadence application.

    Args:
        project_path (Path, optional): Path to a .cadence project file to load. Defaults to None.

    Returns: None
    """
    app = create_app(project_path=project_path)
    app.mainloop()


if __name__ == "__main__":
    run()
