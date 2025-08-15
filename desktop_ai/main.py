import sys
import os
import signal
import logging

from .ui import DesktopAI
from .services import OllamaService
from .core import config
from .core.constants import LOG_FILE
from PyQt6.QtWidgets import QApplication, QMessageBox


def setup_logging():
    """Setup logging configuration."""
    # Configure logging handlers
    handlers = [
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()  # Console output (will be redirected after daemonize)
    ]

    logging.basicConfig(
        handlers=handlers,
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Silence noisy loggers
    for logger_name in ['httpx', 'httpcore', 'ollama']:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def daemonize():
    """Make the process run as a daemon."""
    # First fork
    if os.fork() > 0:
        sys.exit(0)  # Parent exits

    # Decouple from parent environment
    os.chdir("/")
    os.setsid()
    os.umask(0)

    # Second fork to ensure we're not a session leader
    if os.fork() > 0:
        sys.exit(0)  # Second parent exits

    # Redirect standard file descriptors to /dev/null
    sys.stdout.flush()
    sys.stderr.flush()

    null_fd = os.open('/dev/null', os.O_RDWR)
    for fd in (sys.stdin.fileno(), sys.stdout.fileno(), sys.stderr.fileno()):
        os.dup2(null_fd, fd)
    os.close(null_fd)

    logging.info("Desktop AI daemon started")


def validate_requirements():
    """Validate system requirements before starting the application."""
    # Check graphical environment
    if os.getenv('DISPLAY') is None:
        raise EnvironmentError(
            "No graphical environment detected. Desktop AI requires a GUI environment.")

    # Check for Ollama models
    models = OllamaService.get_models()
    if not models:
        raise ValueError(
            "No Ollama models were found. Please install a model to continue.")

    # Set default model if needed
    if not config.model:
        config.model = models[0]
        logging.info(f"Using default model: {config.model}")


def show_error_dialog(title, message):
    """Show error dialog if possible."""
    try:
        app = QApplication(sys.argv)
        QMessageBox.critical(None, title, message)
    except:
        # If we can't show the dialog, just log it
        logging.error(f"{title}: {message}")


def main():
    """Main entry point with error handling."""
    setup_logging()

    try:
        # Validate requirements before daemonizing
        validate_requirements()

        # Daemonize the process
        daemonize()

        # Create QApplication and run the desktop AI
        app = QApplication(sys.argv)
        desktop_ai = DesktopAI(app)

        # Setup signal handlers
        def signal_handler(signum, frame):
            logging.info(f"Received signal {signum}, shutting down...")
            app.quit()

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        logging.info("Desktop AI starting up...")
        exit_code = desktop_ai.run()
        logging.info("Desktop AI shutting down...")
        sys.exit(exit_code)

    except EnvironmentError as e:
        logging.error(str(e))
        print(str(e), file=sys.stderr)
        sys.exit(1)

    except ValueError as e:
        logging.error(str(e))
        show_error_dialog("No Ollama Models Found", str(e))
        sys.exit(1)

    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        logging.error(error_msg, exc_info=True)
        show_error_dialog(
            "Application Error", "An unexpected error occurred. Please check the logs.")
        sys.exit(1)


if __name__ == "__main__":
    main()
