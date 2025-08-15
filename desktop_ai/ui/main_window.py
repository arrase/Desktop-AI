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
import asyncio
from ..agent import ChatAgent  # type: ignore
from .components import APP_STYLESHEET, render_user_message, render_assistant_message  # type: ignore
from ..config.ollama_client import get_available_models_sync
from ..config.config import get_selected_model, set_selected_model


class AgentWorker(QObject):
    """Worker that executes the agent's asynchronous request in a separate thread."""

    response_received = pyqtSignal(str)

    def __init__(self, agent: ChatAgent, prompt: str):
        super().__init__()
        self.agent = agent
        self.prompt = prompt

    def run(self):  # executes within the thread
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                self.agent.get_response(self.prompt))
        finally:
            loop.close()
        self.response_received.emit(response)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.agent = ChatAgent()
        self.setWindowTitle("Chatbot")
        self.resize(800, 600)
        self.setStyleSheet(APP_STYLESHEET)

        # Initialize the thread and worker attributes
        self._thread = None
        self._worker = None

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

        # Load available models
        self.refresh_models()

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

        # Store individual message HTML snippets
        self._messages: list[str] = []

    # ---------------- Internal Helpers ----------------
    def _thread_active(self) -> bool:
        if self._thread is None:
            return False
        try:
            return self._thread.isRunning()
        except RuntimeError:
            self._thread = None
            return False

    def _cleanup_thread(self):  # Qt slot for cleaning up thread references
        self._thread = None
        self._worker = None

    # ---------------- UI Actions ----------------
    def send_message(self):
        user_message = self.input_box.text().strip()
        if not user_message:
            return
        self._append_chat_html(render_user_message(user_message))
        self.input_box.clear()

        # Avoid overlap (could implement queue in the future)
        if self._thread_active():
            return

        self._thread = QThread()
        self._worker = AgentWorker(self.agent, user_message)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.response_received.connect(self.handle_response)
        self._worker.response_received.connect(self._thread.quit)
        self._worker.response_received.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._cleanup_thread)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()
        self.send_button.setEnabled(False)
        self.input_box.setEnabled(False)

    def handle_response(self, response: str):
        self._append_chat_html(render_assistant_message(response))
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
        models = get_available_models_sync()
        current_selection = self.model_selector.currentText()

        # Clear and repopulate the combo box
        self.model_selector.clear()

        if models:
            self.model_selector.addItems(models)

            # Try to restore previous selection
            selected_model = get_selected_model()
            index = self.model_selector.findText(selected_model)
            if index >= 0:
                self.model_selector.setCurrentIndex(index)
            else:
                # If saved model is not available, use first available model
                if models:
                    self.model_selector.setCurrentIndex(0)
                    set_selected_model(models[0])
        else:
            # No models available from Ollama, add default option
            default_model = get_selected_model()
            self.model_selector.addItem(default_model)
            self.model_selector.setCurrentIndex(0)

    def on_model_changed(self, model_name: str):
        """Handle model selection change."""
        if model_name:
            set_selected_model(model_name)
            # Update the agent with the new model
            self.agent.update_model(model_name)
