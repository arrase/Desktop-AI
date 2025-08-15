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
    """Setup logging for daemon mode."""
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Also log to console if not in daemon mode
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)


def daemonize():
    """Make the process run as a daemon."""
    try:
        # First fork to return control to the shell
        pid = os.fork()
        if pid > 0:
            # Parent process, exit
            sys.exit(0)
    except OSError as e:
        logging.error(f"Fork #1 failed: {e}")
        sys.exit(1)

    # Decouple from parent environment
    os.chdir("/")
    os.setsid()
    os.umask(0)

    # Second fork to ensure we're not a session leader
    try:
        pid = os.fork()
        if pid > 0:
            # Exit from second parent
            sys.exit(0)
    except OSError as e:
        logging.error(f"Fork #2 failed: {e}")
        sys.exit(1)

    # Redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()

    # Redirect stdin, stdout, stderr to /dev/null
    with open('/dev/null', 'r') as stdin_null:
        os.dup2(stdin_null.fileno(), sys.stdin.fileno())

    with open('/dev/null', 'w') as stdout_null:
        os.dup2(stdout_null.fileno(), sys.stdout.fileno())

    with open('/dev/null', 'w') as stderr_null:
        os.dup2(stderr_null.fileno(), sys.stderr.fileno())

    logging.info("Desktop AI daemon started")


def main():
    """Main entry point with error handling."""
    # Setup logging first
    setup_logging()

    # Check if we should run as daemon
    run_as_daemon = True

    # Don't daemonize if running in certain environments or with specific arguments
    if (os.getenv('DISPLAY') is None or
        '--no-daemon' in sys.argv or
            '--debug' in sys.argv):
        run_as_daemon = False

    if run_as_daemon:
        daemonize()

    app = QApplication(sys.argv)

    try:
        models = OllamaService.get_models()
        if not models:
            error_msg = "No Ollama models were found. Please install a model to continue."
            logging.error(error_msg)
            if not run_as_daemon:
                QMessageBox.critical(
                    None,
                    "No Ollama Models Found",
                    error_msg,
                )
            sys.exit(1)

        if not config.model:
            config.model = models[0]
            logging.info(f"Using default model: {config.model}")

        desktop_ai = DesktopAI(app)

        # Handle signals gracefully
        def signal_handler(signum, frame):
            logging.info(f"Received signal {signum}, shutting down...")
            app.quit()

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        logging.info("Desktop AI starting up...")
        exit_code = desktop_ai.run()
        logging.info("Desktop AI shutting down...")
        sys.exit(exit_code)

    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        logging.error(error_msg, exc_info=True)
        if not run_as_daemon:
            QMessageBox.critical(
                None,
                "Application Error",
                "An unexpected error occurred. Please check the logs.",
            )
        sys.exit(1)


if __name__ == "__main__":
    main()
