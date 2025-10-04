import sys

from cadence.api.functions import load_project, play, play_sound_file

USAGE = """
Usage: cadence [go|load|play] <options>
Commands:
  go                Launch the Cadence UI
  load <file>       Load a project from a .cadence file and launch the UI
  play <file>       Play a .cadence project file or a .wav audio file
"""


def print_usage():
    """Print the CLI usage information."""
    print(USAGE)


def main():
    """
    Main entry point for the Cadence CLI.

    Parses command-line arguments and launches the appropriate command.
    """
    args = sys.argv[1:]
    if not args or args[0] in {"run", "launch", "lancer", "go"}:
        # Avoid loading UI dependencies unless needed
        from cadence.ui.run import run
        run()
    elif args[0] in {"load"}:
        if len(args) != 2:
            print("Error: 'load' command requires a file path argument.")
            print_usage()
            sys.exit(1)
        file_path = args[1]
        from cadence.ui.run import run
        run(project_path=file_path)
        pass

    elif args[0] in {"play"}:
        if len(args) != 2:
            print(
                "Error: 'play' command requires a path to a .cadence project or a .wav file."
            )
            print_usage()
            sys.exit(1)
        file_path = args[1]

        if file_path.endswith(".cadence"):
            tracks, config = load_project(file_path)
            play(tracks, config)
        elif file_path.endswith(".wav"):
            play_sound_file(file_path)
        else:
            print("Error: Path must be a .cadence project or a .wav file.")
            print_usage()
            sys.exit(1)

    elif args[0] in {"-h", "--help", "help"}:
        print_usage()
        sys.exit(0)

    else:
        print(f"Unknown command: {args[0]}")
        print_usage()
        sys.exit(1)
