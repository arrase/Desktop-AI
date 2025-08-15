import sys
import os
import signal
import logging

from .ui import DesktopAI
from .services import OllamaService
from .core import config
from .core.constants import LOG_FILE
from PyQt6.QtWidgets import QApplication, QMessageBox


def setup_logging(daemon_mode=False):
    """Setup logging for daemon mode."""
    # Configure root logger
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Silence httpx and other noisy loggers
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('ollama').setLevel(logging.WARNING)
    
    # Only add console handler if not in daemon mode
    if not daemon_mode:
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
    # Setup logging first (without console output initially)
    setup_logging(daemon_mode=False)

    # Check if graphical environment is available
    if os.getenv('DISPLAY') is None:
        error_msg = "No graphical environment detected. Desktop AI requires a GUI environment."
        logging.error(error_msg)
        print(error_msg, file=sys.stderr)
        sys.exit(1)

    try:
        # Check for models before daemonizing - do this without QApplication
        models = OllamaService.get_models()
        if not models:
            # Create temporary QApplication just to show the error message
            temp_app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "No Ollama Models Found",
                "No Ollama models were found. Please install a model to continue.",
            )
            sys.exit(1)

        if not config.model:
            config.model = models[0]
            logging.info(f"Using default model: {config.model}")

        # Now that we've verified everything, daemonize
        daemonize()

        # Reconfigure logging for daemon mode (file only)
        setup_logging(daemon_mode=True)

        # Create QApplication in the daemon process
        app = QApplication(sys.argv)
        
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
        # Only try to show QMessageBox if we haven't daemonized yet
        try:
            temp_app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Application Error",
                "An unexpected error occurred. Please check the logs.",
            )
        except:
            # If we can't show the dialog (probably after daemonize), just log it
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
