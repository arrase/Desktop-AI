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

from ..agent import ChatAgent
from ..services import OllamaService, SessionService
from ..core.config import get_config
from ..utils import ThreadManager
from .components import APP_STYLESHEET, render_user_message, render_assistant_message
from .session_history_window import SessionHistoryWindow


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        
        # Initialize config first
        self.config = get_config()
        
        # Initialize agent with the configured model
        self.agent = ChatAgent()
        
        self.session_service = SessionService()
        self.current_session_id = None
        
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
        refresh_button.clicked.connect(self.refresh_models)
        model_row.addWidget(refresh_button)

        reset_button = QPushButton("🗑️")
        reset_button.setToolTip("Reset conversation")
        reset_button.setAccessibleName("Reset conversation")
        reset_button.clicked.connect(self._on_reset_clicked)
        model_row.addWidget(reset_button)

        history_button = QPushButton("📋")
        history_button.setToolTip("Ver historial de conversaciones")
        history_button.setAccessibleName("Ver historial")
        history_button.clicked.connect(self._on_history_clicked)
        model_row.addWidget(history_button)

        # Session status indicator
        self.session_status_label = QLabel("Nueva conversación")
        self.session_status_label.setStyleSheet("color: #8FBCBB; font-size: 11px; padding: 4px;")
        model_row.addWidget(self.session_status_label)

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

    def _clear_chat_history(self):
        """Clears the chat history display and state."""
        self._messages.clear()
        self.chat_history.setHtml(
            "<html><body><div id='chat-root'></div></body></html>")

    def _on_reset_clicked(self):
        """Handle reset button click."""
        self._clear_chat_history()
        self.agent.reset()
        self.current_session_id = None
        self.session_status_label.setText("Nueva conversación")

    def _on_history_clicked(self):
        """Handle history button click."""
        history_window = SessionHistoryWindow(self)
        history_window.session_selected.connect(self._load_session)
        history_window.exec()

    def _load_session(self, session_id: str):
        """Load an existing session and display its messages."""
        try:
            # Load the session in the agent
            self.agent.load_session(session_id)
            self.current_session_id = session_id
            
            # Clear current chat and load session messages
            self._clear_chat_history()
            
            # Get messages from the session service
            messages = self.session_service.get_session_messages(session_id)
            
            # Display the messages
            for message in messages:
                role = message.get('role', '')
                content = message.get('content', '')
                
                if role == 'user':
                    self._append_chat_html(render_user_message(content))
                elif role == 'assistant':
                    # Extract text content from assistant message structure
                    if isinstance(content, list) and len(content) > 0:
                        if isinstance(content[0], dict) and 'text' in content[0]:
                            text_content = content[0]['text']
                        else:
                            text_content = str(content)
                    else:
                        text_content = str(content)
                    self._append_chat_html(render_assistant_message(text_content))
            
            # Update session status
            self.session_status_label.setText(f"Conversación cargada ({session_id[:8]}...)")
            
        except Exception as e:
            self._append_chat_html(render_assistant_message(f"Error cargando la sesión: {e}"))

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
            self._clear_chat_history()
            self.current_session_id = None
            self.session_status_label.setText("Nueva conversación")
