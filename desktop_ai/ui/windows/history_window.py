"""History window."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
    QListWidgetItem, QPushButton, QLabel, QMessageBox,
    QWidget, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ...services import SessionService, SessionInfo
from ..styles import STYLESHEET
from ..widgets import ChatWidget


class SessionListItem(QWidget):
    """Custom session list item."""
    
    def __init__(self, session_info: SessionInfo):
        super().__init__()
        self.session_info = session_info
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        # Title
        title = QLabel(self.session_info.get_display_name())
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title.setFont(title_font)
        title.setWordWrap(True)
        layout.addWidget(title)

        # Info row
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        count_label = QLabel(f"{self.session_info.message_count} messages")
        count_label.setStyleSheet("color: #8FBCBB; font-size: 9px;")
        info_layout.addWidget(count_label)
        
        info_layout.addStretch()
        
        time_label = QLabel(self.session_info.get_relative_time())
        time_label.setStyleSheet("color: #8FBCBB; font-size: 9px;")
        info_layout.addWidget(time_label)
        
        layout.addLayout(info_layout)


class HistoryWindow(QDialog):
    """Conversation history window."""
    
    session_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.session_service = SessionService()
        self.current_session_id = None
        
        self.setWindowTitle("Conversation History")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(STYLESHEET)
        
        self._setup_ui()
        self._load_sessions()

    def _setup_ui(self):
        """Setup UI."""
        layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Session list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("Recent Conversations"))
        
        self.session_list = QListWidget()
        self.session_list.setMinimumWidth(300)
        self.session_list.itemClicked.connect(self._on_session_selected)
        left_layout.addWidget(self.session_list)
        
        # Buttons
        buttons = QHBoxLayout()
        
        self.load_btn = QPushButton("Load")
        self.load_btn.setEnabled(False)
        self.load_btn.clicked.connect(self._load_session)
        buttons.addWidget(self.load_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self._delete_session)
        buttons.addWidget(self.delete_btn)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.clicked.connect(self._load_sessions)
        buttons.addWidget(refresh_btn)
        
        left_layout.addLayout(buttons)
        
        # Right panel - Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.preview_header = QLabel("Preview")
        right_layout.addWidget(self.preview_header)
        
        self.preview_area = ChatWidget()
        self.preview_area.setMinimumWidth(400)
        right_layout.addWidget(self.preview_area)
        
        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_layout.addWidget(close_btn)
        right_layout.addLayout(close_layout)
        
        # Add to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 500])

    def _load_sessions(self):
        """Load sessions from database."""
        self.session_list.clear()
        sessions = self.session_service.get_sessions()
        
        for session in sessions:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, session.session_id)
            
            widget = SessionListItem(session)
            item.setSizeHint(widget.sizeHint())
            
            self.session_list.addItem(item)
            self.session_list.setItemWidget(item, widget)
        
        if not sessions:
            self.preview_area.clear_chat()
            # No need to show a message as the empty chat area is clear enough

    def _on_session_selected(self, item: QListWidgetItem):
        """Handle session selection."""
        session_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_session_id = session_id
        
        self.load_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        
        self._load_preview(session_id)

    def _load_preview(self, session_id: str):
        """Load session preview."""
        messages = self.session_service.get_messages(session_id)
        
        if not messages:
            self.preview_area.clear_chat()
            return
        
        # Update header
        for i in range(self.session_list.count()):
            item = self.session_list.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == session_id:
                widget = self.session_list.itemWidget(item)
                if isinstance(widget, SessionListItem):
                    self.preview_header.setText(
                        f"Preview - {widget.session_info.get_relative_time()}"
                    )
                    break
        
        # Clear previous messages
        self.preview_area.clear_chat()
        
        # Add messages to the chat widget
        for message in messages:
            role = message.get('role', '')
            content = message.get('content', '')
            
            if role == 'user':
                self.preview_area.add_user_message(content)
            elif role == 'assistant':
                # Handle complex content structure
                if isinstance(content, list) and len(content) > 0:
                    if isinstance(content[0], dict) and 'text' in content[0]:
                        text_content = content[0]['text']
                    else:
                        text_content = str(content)
                else:
                    text_content = str(content)
                self.preview_area.add_assistant_message(text_content)

    def _load_session(self):
        """Load selected session."""
        if self.current_session_id:
            self.session_selected.emit(self.current_session_id)
            self.accept()

    def _delete_session(self):
        """Delete selected session."""
        if not self.current_session_id:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Delete this conversation?\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self.session_service.delete_session(self.current_session_id)
            
            if success:
                self._load_sessions()
                self.current_session_id = None
                self.load_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
                self.preview_area.clear_chat()
                self.preview_header.setText("Preview")
            else:
                QMessageBox.warning(self, "Error", "Could not delete conversation.")
