import sys
from .ui import DesktopAI


def main():
    """Main entry point with error handling."""
    try:
        app = DesktopAI(sys.argv)
        app.run()
    except Exception as e:
        sys.exit(1)


if __name__ == "__main__":
    main()
