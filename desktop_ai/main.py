import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from .ui import DesktopAI
from .services import OllamaService
from .core import config


def main():
    """Main entry point with error handling."""
    app = QApplication(sys.argv)

    try:
        models = OllamaService.get_models()
        if not models:
            QMessageBox.critical(
                None,
                "No Ollama Models Found",
                "No Ollama models were found. Please install a model to continue.",
            )
            sys.exit(1)

        if not config.model:
            config.model = models[0]

        desktop_ai = DesktopAI(app)
        desktop_ai.run()
    except Exception:
        QMessageBox.critical(
            None,
            "Application Error",
            "An unexpected error occurred. Please check the logs.",
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
