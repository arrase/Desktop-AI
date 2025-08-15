"""Settings window for the application."""
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QWidget,
)
from ..core.config import get_config
from ..agent.chat_agent import ChatAgent


class SettingsWindow(QDialog):
    def __init__(self, agent: ChatAgent, parent=None):
        super().__init__(parent)
        self.agent = agent
        self.config = get_config()

        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # System Prompt section
        prompt_label = QLabel("System Prompt:")
        layout.addWidget(prompt_label)

        self.prompt_text_edit = QTextEdit()
        self.prompt_text_edit.setPlaceholderText("Enter the system prompt here...")
        layout.addWidget(self.prompt_text_edit)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _load_settings(self):
        """Load settings from config and populate the UI."""
        self.prompt_text_edit.setText(self.config.system_prompt)

    def save_settings(self):
        """Save the current settings and close the dialog."""
        new_prompt = self.prompt_text_edit.toPlainText().strip()
        if new_prompt and new_prompt != self.config.system_prompt:
            self.config.system_prompt = new_prompt
            self.agent.update_system_prompt(new_prompt)
        self.accept()
