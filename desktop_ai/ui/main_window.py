"""Main application chat window."""
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QComboBox,
    QLabel,
)
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtCore import QThread, pyqtSignal, QObject

from ..agent import ChatAgent
from ..services import OllamaService
from ..core.config import get_config
from ..utils import ThreadManager
from .components import APP_STYLESHEET, render_user_message, render_assistant_message


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        
        # Initialize config first
        self.config = get_config()
        
        # Initialize agent with the configured model
        self.agent = ChatAgent()
        
        self.thread_manager = ThreadManager()
        
        self.setWindowTitle("Chatbot")
        self.resize(800, 600)
        self.setStyleSheet(APP_STYLESHEET)

        self._setup_ui()
        self.refresh_models()

        # Store individual message HTML snippets
        self._messages: list[str] = []

    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Model selector at the top
        model_row = QHBoxLayout()
        model_label = QLabel("Model:")
        model_row.addWidget(model_label)

        self.model_selector = QComboBox()
        self.model_selector.setToolTip("Select the AI model to use")
        self.model_selector.currentTextChanged.connect(self.on_model_changed)
        model_row.addWidget(self.model_selector)

        refresh_button = QPushButton("🔄")
        refresh_button.setToolTip("Refresh model list")
        refresh_button.setMaximumWidth(40)
        refresh_button.clicked.connect(self.refresh_models)
        model_row.addWidget(refresh_button)

        model_row.addStretch()  # Push everything to the left
        layout.addLayout(model_row)

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setHtml(
            "<html><body><div id='chat-root'></div></body></html>")
        layout.addWidget(self.chat_history)

        input_row = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type a message and press Enter…")
        self.input_box.returnPressed.connect(self.send_message)
        input_row.addWidget(self.input_box, stretch=1)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_row.addWidget(self.send_button)

        layout.addLayout(input_row)

    # ---------------- UI Actions ----------------
    def send_message(self):
        user_message = self.input_box.text().strip()
        if not user_message:
            return
        
        self._append_chat_html(render_user_message(user_message))
        self.input_box.clear()

        # Avoid overlap - check if already processing
        if self.thread_manager.is_active():
            return

        # Start async task
        try:
            worker = self.thread_manager.start_async_task(
                self.agent.get_response, user_message
            )
            worker.result_ready.connect(self.handle_response)
            worker.error_occurred.connect(self.handle_error)
            
            self.send_button.setEnabled(False)
            self.input_box.setEnabled(False)
        except RuntimeError:
            # Task already running, ignore
            pass

    def handle_response(self, response: str):
        """Handle successful response from agent."""
        self._append_chat_html(render_assistant_message(response))
        self._enable_input()

    def handle_error(self, error: str):
        """Handle error from agent."""
        self._append_chat_html(render_assistant_message(f"Error: {error}"))
        self._enable_input()

    def _enable_input(self):
        """Re-enable input controls."""
        self.send_button.setEnabled(True)
        self.input_box.setEnabled(True)
        self.input_box.setFocus()

    def _append_chat_html(self, snippet: str):
        """Append a bubble snippet rebuilding the whole document (simple approach)."""
        self._messages.append(snippet)
        html_doc = (
            "<html><body><div id='chat-root'>" +
            "".join(self._messages) + "</div></body></html>"
        )
        self.chat_history.setHtml(html_doc)
        # Auto scroll to bottom
        sb = self.chat_history.verticalScrollBar()
        if sb is not None:
            sb.setValue(sb.maximum())

    # ---------------- Events ----------------
    def closeEvent(self, event: QCloseEvent):  # type: ignore[override]
        self.hide()
        event.ignore()

    # ---------------- Model Management ----------------
    def refresh_models(self):
        """Refresh the list of available models from Ollama."""
        # Temporarily disconnect the signal to avoid triggering on_model_changed during setup
        self.model_selector.currentTextChanged.disconnect()
        
        models = OllamaService.get_available_models_sync()
        
        # Clear and repopulate the combo box
        self.model_selector.clear()

        if models:
            self.model_selector.addItems(models)

            # Try to restore previous selection from config
            selected_model = self.config.selected_model
            index = self.model_selector.findText(selected_model)
            if index >= 0:
                self.model_selector.setCurrentIndex(index)
            else:
                # If saved model is not available, use first available model
                self.model_selector.setCurrentIndex(0)
                # Update config to reflect the new selection
                self.config.selected_model = models[0]
                # Update agent to use the new model
                self.agent.update_model(models[0])
        else:
            # No models available from Ollama, add default option
            default_model = self.config.selected_model
            self.model_selector.addItem(default_model)
            self.model_selector.setCurrentIndex(0)
        
        # Reconnect the signal after setup is complete
        self.model_selector.currentTextChanged.connect(self.on_model_changed)

    def on_model_changed(self, model_name: str):
        """Handle model selection change."""
        if model_name and model_name != self.config.selected_model:
            self.config.selected_model = model_name
            # Update the agent with the new model
            self.agent.update_model(model_name)
