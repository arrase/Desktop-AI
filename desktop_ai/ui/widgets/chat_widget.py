"""Modern chat display widget using native Qt widgets."""
from typing import List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
    QFrame, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import markdown2


class MessageBubble(QFrame):
    """Individual message bubble widget."""
    
    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        # Set transparent background for the container
        self.setStyleSheet("QFrame { background: transparent; border: none; }")
        self.setup_ui(text)
    
    def setup_ui(self, text: str):
        """Setup the bubble UI."""
        # Main container layout
        container_layout = QHBoxLayout(self)
        container_layout.setContentsMargins(10, 5, 10, 5)
        
        if self.is_user:
            # User message: add spacer first, then bubble (align right)
            container_layout.addItem(QSpacerItem(80, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            
            # Create the bubble frame
            bubble_frame = QFrame()
            bubble_frame.setStyleSheet("""
                QFrame {
                    background-color: #89b4fa;
                    color: #11111b;
                    border-radius: 15px;
                    padding: 12px 16px;
                    max-width: 400px;
                }
            """)
            
            # Bubble layout
            bubble_layout = QHBoxLayout(bubble_frame)
            bubble_layout.setContentsMargins(0, 0, 0, 0)
            
            # Create the message label
            message_label = QLabel(text)
            message_label.setWordWrap(True)
            message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            message_label.setStyleSheet("background: transparent; color: #11111b; font-weight: 600; font-size: 14px;")
            message_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            
            # Set font
            font = QFont("Segoe UI", 10)
            font.setWeight(QFont.Weight.Medium)
            message_label.setFont(font)
            
            bubble_layout.addWidget(message_label)
            container_layout.addWidget(bubble_frame)
            
        else:
            # Assistant message: bubble first, then spacer (align left)
            
            # Create the bubble frame
            bubble_frame = QFrame()
            bubble_frame.setStyleSheet("""
                QFrame {
                    background-color: #313244;
                    color: #cdd6f4;
                    border-radius: 15px;
                    border: 1px solid #45475a;
                    padding: 12px 16px;
                    max-width: 400px;
                }
            """)
            
            # Bubble layout
            bubble_layout = QHBoxLayout(bubble_frame)
            bubble_layout.setContentsMargins(0, 0, 0, 0)
            
            # Create the message label
            message_label = QLabel()
            message_label.setWordWrap(True)
            message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            message_label.setStyleSheet("background: transparent; color: #cdd6f4; font-size: 14px;")
            message_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            
            # Set font
            font = QFont("Segoe UI", 10)
            message_label.setFont(font)
            
            # Process markdown for assistant messages
            if any(marker in text for marker in ['```', '**', '*', '#', '`']):
                html_content = markdown2.markdown(text, extras=["fenced-code-blocks"])
                # Simple styling for code blocks
                html_content = html_content.replace(
                    '<pre>', '<pre style="background-color: #11111b; padding: 8px; border-radius: 6px; margin: 4px 0; color: #cdd6f4; font-family: monospace;">'
                ).replace(
                    '<code>', '<code style="background-color: #45475a; padding: 2px 4px; border-radius: 3px; color: #fab387; font-family: monospace;">'
                )
                message_label.setText(html_content)
            else:
                message_label.setText(text)
            
            bubble_layout.addWidget(message_label)
            container_layout.addWidget(bubble_frame)
            container_layout.addItem(QSpacerItem(80, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))


class ChatWidget(QScrollArea):
    """Modern chat display widget using native Qt widgets."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setSpacing(8)
        self.messages_layout.setContentsMargins(10, 10, 10, 10)
        
        # Setup scroll area
        self.setWidget(self.messages_widget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Style the scroll area
        self.setStyleSheet("""
            QScrollArea {
                background-color: #181825;
                border: none;
            }
            QWidget {
                background-color: #181825;
            }
        """)
        
        # Add stretch at the end to push messages to the top
        self.messages_layout.addStretch()
    
    def add_user_message(self, text: str):
        """Add user message."""
        # Remove the stretch temporarily
        self.messages_layout.takeAt(self.messages_layout.count() - 1)
        
        # Add the message
        bubble = MessageBubble(text, is_user=True)
        self.messages_layout.addWidget(bubble)
        
        # Add stretch back
        self.messages_layout.addStretch()
        
        # Scroll to bottom
        self.scroll_to_bottom()
    
    def add_assistant_message(self, text: str):
        """Add assistant message."""
        # Remove the stretch temporarily
        self.messages_layout.takeAt(self.messages_layout.count() - 1)
        
        # Add the message
        bubble = MessageBubble(text, is_user=False)
        self.messages_layout.addWidget(bubble)
        
        # Add stretch back
        self.messages_layout.addStretch()
        
        # Scroll to bottom
        self.scroll_to_bottom()
    
    def clear_chat(self):
        """Clear all messages."""
        # Remove all widgets except the stretch
        while self.messages_layout.count() > 1:
            child = self.messages_layout.takeAt(0)
            if child and child.widget():
                child.widget().deleteLater()
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the chat."""
        # Force update the layout
        self.messages_widget.updateGeometry()
        # Scroll to bottom after a brief delay to ensure layout is updated
        scrollbar = self.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())
