"""Settings window."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPushButton, QLabel
)

from ...core import config
from ...agent import ChatAgent
from ..styles import STYLESHEET


class SettingsWindow(QDialog):
    """Settings configuration window."""

    def __init__(self, agent: ChatAgent, parent=None):
        super().__init__(parent)
        self.agent = agent
        
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 300)
        self.setStyleSheet(STYLESHEET)
        
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)

        # System prompt
        layout.addWidget(QLabel("System Prompt:"))
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter system prompt...")
        layout.addWidget(self.prompt_edit)

        # Buttons
        buttons = QHBoxLayout()
        buttons.addStretch()

        save_btn = QPushButton("Save")
        save_btn.setObjectName("sendButton")  # Use primary button style
        save_btn.clicked.connect(self._save_settings)
        buttons.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("historyButton")  # Use secondary button style
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)

    def _load_settings(self):
        """Load current settings."""
        self.prompt_edit.setText(config.system_prompt)

    def _save_settings(self):
        """Save settings."""
        new_prompt = self.prompt_edit.toPlainText().strip()
        if new_prompt and new_prompt != config.system_prompt:
            config.system_prompt = new_prompt
            self.agent.update_system_prompt(new_prompt)
        self.accept()
