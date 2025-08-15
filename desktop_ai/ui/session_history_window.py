"""Session history window for managing conversation history."""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QMessageBox,
    QWidget,
    QSplitter,
    QTextEdit,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..services import SessionService, SessionInfo
from .components import APP_STYLESHEET, render_user_message, render_assistant_message


class SessionListItem(QWidget):
    """Custom widget for displaying session information in the list."""
    
    def __init__(self, session_info: SessionInfo):
        super().__init__()
        self.session_info = session_info
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        # Main title (preview of first message)
        title_label = QLabel(self.session_info.get_display_name())
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        # Info row with message count and time
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        message_count_label = QLabel(f"{self.session_info.message_count} messages")
        message_count_label.setStyleSheet("color: #8FBCBB; font-size: 9px;")
        info_layout.addWidget(message_count_label)
        
        info_layout.addStretch()
        
        time_label = QLabel(self.session_info.get_relative_time())
        time_label.setStyleSheet("color: #8FBCBB; font-size: 9px;")
        info_layout.addWidget(time_label)
        
        layout.addLayout(info_layout)


class SessionHistoryWindow(QDialog):
    """Window for viewing and managing conversation history."""
    
    session_selected = pyqtSignal(str)  # Emits session_id when a session is selected for loading
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.session_service = SessionService()
        self.current_session_id = None
        
        self.setWindowTitle("Conversation History")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        self.setStyleSheet(APP_STYLESHEET)
        
        self._setup_ui()
        self._load_sessions()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QHBoxLayout(self)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Session list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # List header
        list_header = QLabel("Recent Conversations")
        list_header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 8px;")
        left_layout.addWidget(list_header)
        
        # Session list
        self.session_list = QListWidget()
        self.session_list.setMinimumWidth(300)
        self.session_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.session_list.itemClicked.connect(self._on_session_selected)
        left_layout.addWidget(self.session_list)
        
        # Buttons for session management
        button_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Load Conversation")
        self.load_button.setEnabled(False)
        self.load_button.clicked.connect(self._on_load_session)
        button_layout.addWidget(self.load_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self._on_delete_session)
        button_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setToolTip("Refresh List")
        self.refresh_button.clicked.connect(self._load_sessions)
        button_layout.addWidget(self.refresh_button)
        
        left_layout.addLayout(button_layout)
        
        # Right panel - Session preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Preview header
        self.preview_header = QLabel("Preview")
        self.preview_header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 8px;")
        right_layout.addWidget(self.preview_header)
        
        # Message preview area
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setMinimumWidth(400)
        right_layout.addWidget(self.preview_area)
        
        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_layout.addWidget(close_button)
        
        right_layout.addLayout(close_layout)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set initial splitter sizes (30% left, 70% right)
        splitter.setSizes([300, 700])

    def _load_sessions(self):
        """Load sessions from the database and populate the list."""
        self.session_list.clear()
        sessions = self.session_service.get_all_sessions()
        
        for session in sessions:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, session.session_id)
            
            widget = SessionListItem(session)
            item.setSizeHint(widget.sizeHint())
            
            self.session_list.addItem(item)
            self.session_list.setItemWidget(item, widget)
        
        # Clear preview if no sessions
        if not sessions:
            self.preview_area.setHtml("<p style='color: #8FBCBB; text-align: center; margin-top: 50px;'>No saved conversations</p>")
            self.preview_header.setText("Preview")

    def _on_session_selected(self, item: QListWidgetItem):
        """Handle session selection."""
        session_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_session_id = session_id
        
        # Enable buttons
        self.load_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        
        # Load and display session preview
        self._load_session_preview(session_id)

    def _load_session_preview(self, session_id: str):
        """Load and display preview of the selected session."""
        messages = self.session_service.get_session_messages(session_id)
        
        if not messages:
            self.preview_area.setHtml("<p style='color: #BF616A;'>Error loading messages for this conversation</p>")
            return
        
        # Update header with session info
        session_info = None
        for i in range(self.session_list.count()):
            item = self.session_list.item(i)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) == session_id:
                widget = self.session_list.itemWidget(item)
                if isinstance(widget, SessionListItem):
                    session_info = widget.session_info
                    break
        
        if session_info:
            self.preview_header.setText(f"Preview - {session_info.get_relative_time()}")
        
        # Render messages
        html_messages = []
        for message in messages:
            role = message.get('role', '')
            content = message.get('content', '')
            
            if role == 'user':
                html_messages.append(render_user_message(content))
            elif role == 'assistant':
                # Extract text content from assistant message structure
                if isinstance(content, list) and len(content) > 0:
                    if isinstance(content[0], dict) and 'text' in content[0]:
                        text_content = content[0]['text']
                    else:
                        text_content = str(content)
                else:
                    text_content = str(content)
                html_messages.append(render_assistant_message(text_content))
        
        # Display messages
        html_doc = (
            "<html><body><div id='chat-root'>" +
            "".join(html_messages) + 
            "</div></body></html>"
        )
        self.preview_area.setHtml(html_doc)

    def _on_load_session(self):
        """Handle loading a session into the main chat."""
        if self.current_session_id:
            self.session_selected.emit(self.current_session_id)
            self.accept()

    def _on_delete_session(self):
        """Handle session deletion."""
        if not self.current_session_id:
            return
        
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this conversation?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self.session_service.delete_session(self.current_session_id)
            
            if success:
                # Reload the session list
                self._load_sessions()
                self.current_session_id = None
                self.load_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                self.preview_area.setHtml("<p style='color: #8FBCBB; text-align: center; margin-top: 50px;'>Conversation deleted</p>")
                self.preview_header.setText("Preview")
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Could not delete the conversation. Please try again."
                )
