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
    try:
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

    except OSError as e:
        logging.error(f"Daemonization failed: {e}")
        sys.exit(1)

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
    if not os.getenv('DISPLAY'):
        raise EnvironmentError(
            "No graphical environment detected. Desktop AI requires a GUI environment.")

    # Check for Ollama models
    try:
        models = OllamaService.get_models()
    except Exception as e:
        raise ConnectionError(f"Failed to connect to Ollama service: {e}")
    
    if not models:
        raise ValueError(
            "No Ollama models were found. Please install a model to continue.")

    # Set default model if needed
    if not config.model:
        config.model = models[0]
        logging.info(f"Using default model: {config.model}")
    elif config.model not in models:
        logging.warning(f"Configured model '{config.model}' not found, using '{models[0]}'")
        config.model = models[0]


def show_error_dialog(title, message):
    """Show error dialog if possible, otherwise just log."""
    try:
        # Only create QApplication if one doesn't exist
        if not QApplication.instance():
            QApplication(sys.argv)
        QMessageBox.critical(None, title, message)
    except Exception:
        # If we can't show the dialog, just log it
        logging.error(f"{title}: {message}")


def setup_signal_handlers(app):
    """Setup graceful shutdown signal handlers."""
    def signal_handler(signum, frame):
        logging.info(f"Received signal {signum}, shutting down...")
        app.quit()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


# Exit codes
EXIT_SUCCESS = 0
EXIT_ENV_ERROR = 1
EXIT_MODEL_ERROR = 2
EXIT_CONNECTION_ERROR = 3
EXIT_GENERAL_ERROR = 4


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
        setup_signal_handlers(app)

        logging.info("Desktop AI starting up...")
        exit_code = desktop_ai.run()
        logging.info("Desktop AI shutting down...")
        sys.exit(exit_code or EXIT_SUCCESS)

    except ConnectionError as e:
        logging.error(f"Connection error: {e}")
        show_error_dialog("Connection Error", str(e))
        sys.exit(EXIT_CONNECTION_ERROR)

    except EnvironmentError as e:
        logging.error(f"Environment error: {e}")
        print(f"Environment error: {e}", file=sys.stderr)
        sys.exit(EXIT_ENV_ERROR)

    except ValueError as e:
        logging.error(f"Model error: {e}")
        show_error_dialog("No Ollama Models Found", str(e))
        sys.exit(EXIT_MODEL_ERROR)

    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logging.error(error_msg, exc_info=True)
        show_error_dialog("Application Error", 
                         "An unexpected error occurred. Please check the logs.")
        sys.exit(EXIT_GENERAL_ERROR)


if __name__ == "__main__":
    main()
