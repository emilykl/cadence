import os
from pathlib import Path
import sys

WHICH_PYTHON = Path(sys.executable).resolve()

TKINTER_ERROR_MSG = f"""

Error: tkinter (Python's GUI library) could not be loaded.

You may need to install tkinter separately if it was not included
with your Python installation.

If you're on Mac and you've installed Python via Homebrew,
then you can install tkinter with:

    $ brew install python-tk      # or possibly python-tk@3.x for your version of Python

On Debian-based systems (like Ubuntu), you can install it with:

    $ sudo apt-get install python3-tk

This installation of Python is located at:
{WHICH_PYTHON}
"""


def check_tkinter():
    """
    Check if tkinter is available. If not, try to set environment variables to fix it.
    If it still fails, raise an error with instructions.
    """

    try:
        import tkinter as _tkinter
        _ = _tkinter.Tcl()
    except (ModuleNotFoundError, _tkinter.TclError):
        # Sometimes tkinter paths are not set correctly in virtual environments
        # We can try to fix this by setting the path manually but it might not work
        # TODO: Below fix only works for Mac in any case, need to make cross-platform
        # Reference: https://github.com/astral-sh/uv/issues/7036
        os.environ["TCL_LIBRARY"] = str(Path(sys.base_prefix) / "lib" / "tcl8.6")
        os.environ["TK_LIBRARY"] = str(Path(sys.base_prefix) / "lib" / "tk8.6")
        try:
            import tkinter as _tkinter
            _ = _tkinter.Tcl()
        except (ModuleNotFoundError, _tkinter.TclError):
            raise RuntimeError(TKINTER_ERROR_MSG)
    
    os.environ["TCL_LIBRARY"] = str(Path(sys.base_prefix) / "lib" / "tcl8.6")
    os.environ["TK_LIBRARY"] = str(Path(sys.base_prefix) / "lib" / "tk8.6")
