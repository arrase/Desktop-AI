"""Main chat window."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QComboBox, QLabel
)

from ...agent import ChatAgent
from ...services import OllamaService, SessionService
from ...core import config
from ...utils import ThreadManager
from ..widgets import ChatWidget
from ..styles import STYLESHEET


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.agent = ChatAgent()
        self.session_service = SessionService()
        self.thread_manager = ThreadManager()
        self.current_session_id = None
        
        # Setup UI
        self.setWindowTitle("Desktop AI")
        self.resize(800, 600)
        self.setStyleSheet(STYLESHEET)
        self._setup_ui()
        self._refresh_models()

    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Top controls
        controls = QHBoxLayout()
        
        # Model selector
        controls.addWidget(QLabel("Model:"))
        self.model_selector = QComboBox()
        self.model_selector.setToolTip("Select AI model")
        self.model_selector.currentTextChanged.connect(self._on_model_changed)
        controls.addWidget(self.model_selector)

        # Buttons
        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Refresh models")
        refresh_btn.clicked.connect(self._refresh_models)
        controls.addWidget(refresh_btn)

        reset_btn = QPushButton("🗑️")
        reset_btn.setToolTip("Reset conversation")
        reset_btn.clicked.connect(self._reset_chat)
        controls.addWidget(reset_btn)
        
        history_btn = QPushButton("📋")
        history_btn.setToolTip("View history")
        history_btn.clicked.connect(self._show_history)
        controls.addWidget(history_btn)

        controls.addStretch()
        layout.addLayout(controls)

        # Chat display
        self.chat_widget = ChatWidget()
        layout.addWidget(self.chat_widget)

        # Input area
        input_layout = QHBoxLayout()
        
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type a message...")
        self.input_box.returnPressed.connect(self._send_message)
        input_layout.addWidget(self.input_box, stretch=1)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

    def _send_message(self):
        """Send a message to the agent."""
        text = self.input_box.text().strip()
        if not text or self.thread_manager.is_active():
            return
        
        # Add user message and clear input
        self.chat_widget.add_user_message(text)
        self.input_box.clear()
        
        # Disable input while processing
        self._set_input_enabled(False)
        
        # Start async task
        try:
            worker = self.thread_manager.start_task(self.agent.get_response, text)
            worker.result_ready.connect(self._handle_response)
            worker.error_occurred.connect(self._handle_error)
        except RuntimeError:
            self._set_input_enabled(True)

    def _handle_response(self, response: str):
        """Handle agent response."""
        self.chat_widget.add_assistant_message(response)
        self._set_input_enabled(True)

    def _handle_error(self, error: str):
        """Handle error."""
        self.chat_widget.add_assistant_message(f"Error: {error}")
        self._set_input_enabled(True)

    def _set_input_enabled(self, enabled: bool):
        """Enable/disable input controls."""
        self.send_button.setEnabled(enabled)
        self.input_box.setEnabled(enabled)
        if enabled:
            self.input_box.setFocus()

    def _refresh_models(self):
        """Refresh available models."""
        # Temporarily disconnect signal
        self.model_selector.currentTextChanged.disconnect()
        
        models = OllamaService.get_models()
        self.model_selector.clear()

        if models:
            self.model_selector.addItems(models)
            # Try to restore previous selection
            if config.model in models:
                self.model_selector.setCurrentText(config.model)
            else:
                # Use first available model
                config.model = models[0]
                self.agent.update_model(models[0])
        else:
            # No models available, add current config model
            self.model_selector.addItem(config.model)
        
        # Reconnect signal
        self.model_selector.currentTextChanged.connect(self._on_model_changed)

    def _on_model_changed(self, model_name: str):
        """Handle model change."""
        if model_name and model_name != config.model:
            config.model = model_name
            self.agent.update_model(model_name)
            self._reset_chat()

    def _reset_chat(self):
        """Reset the conversation."""
        self.chat_widget.clear_chat()
        self.agent.reset()
        self.current_session_id = None

    def _show_history(self):
        """Show conversation history."""
        from .history_window import HistoryWindow
        dialog = HistoryWindow(self)
        dialog.session_selected.connect(self._load_session)
        dialog.exec()

    def _load_session(self, session_id: str):
        """Load a session."""
        try:
            self.agent.load_session(session_id)
            self.current_session_id = session_id
            
            # Clear and load messages
            self.chat_widget.clear_chat()
            messages = self.session_service.get_messages(session_id)
            
            for message in messages:
                role = message.get('role', '')
                content = message.get('content', '')
                
                if role == 'user':
                    self.chat_widget.add_user_message(content)
                elif role == 'assistant':
                    # Handle complex content structure
                    if isinstance(content, list) and len(content) > 0:
                        if isinstance(content[0], dict) and 'text' in content[0]:
                            text_content = content[0]['text']
                        else:
                            text_content = str(content)
                    else:
                        text_content = str(content)
                    self.chat_widget.add_assistant_message(text_content)
                    
        except Exception as e:
            self.chat_widget.add_assistant_message(f"Error loading session: {e}")

    def closeEvent(self, a0):
        """Handle close event - minimize to tray."""
        self.hide()
        if a0:
            a0.ignore()
