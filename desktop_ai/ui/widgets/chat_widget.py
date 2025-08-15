"""Modern chat display widget using native Qt widgets."""
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
    QFrame, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import markdown2

# Compile regex pattern once at module level for better performance
MARKDOWN_PATTERN = re.compile(r'```|`|\*\*|\*|#{1,6}\s|^\s*[-*+]\s|^\s*\d+\.\s', re.MULTILINE)


class MarkdownStyler:
    """Handles markdown styling and HTML formatting."""
    
    # CSS-like styles for different HTML elements
    STYLES = {
        'pre': 'background-color: #11111b; padding: 12px; border-radius: 8px; margin: 8px 0; color: #cdd6f4; font-family: \'JetBrains Mono\', Consolas, monospace; font-size: 13px; line-height: 1.4; border: 1px solid #45475a;',
        'code': 'background-color: #45475a; padding: 3px 6px; border-radius: 4px; color: #fab387; font-family: \'JetBrains Mono\', Consolas, monospace; font-size: 13px;',
        'h1': 'color: #cdd6f4; font-size: 18px; font-weight: bold; margin: 12px 0 8px 0;',
        'h2': 'color: #cdd6f4; font-size: 16px; font-weight: bold; margin: 10px 0 6px 0;',
        'h3': 'color: #cdd6f4; font-size: 14px; font-weight: bold; margin: 8px 0 4px 0;',
        'strong': 'color: #fab387; font-weight: bold;',
        'em': 'color: #a6e3a1; font-style: italic;'
    }
    
    @classmethod
    def has_markdown(cls, text: str) -> bool:
        """Efficiently detect if text contains markdown formatting."""
        return bool(MARKDOWN_PATTERN.search(text))
    
    @classmethod
    def apply_styles(cls, html_content: str) -> str:
        """Apply consistent styling to HTML elements."""
        for tag, style in cls.STYLES.items():
            html_content = html_content.replace(f'<{tag}>', f'<{tag} style="{style}">')
        return html_content
    
    @classmethod
    def process_markdown(cls, text: str) -> str:
        """Process markdown text and apply styling."""
        if not cls.has_markdown(text):
            return text
        
        html_content = markdown2.markdown(text, extras=["fenced-code-blocks", "tables"])
        return cls.apply_styles(html_content)


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
            # Spacer takes 30% of space, bubble takes the rest
            container_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            
            # Create the bubble frame
            bubble_frame = QFrame()
            bubble_frame.setStyleSheet("""
                QFrame {
                    background-color: #45475a;
                    color: #cdd6f4;
                    border-radius: 15px;
                    border: 1px solid #6c7086;
                    padding: 12px 16px;
                }
            """)
            
            # Create the message label
            message_label = QLabel()
            message_label.setWordWrap(True)
            message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            message_label.setStyleSheet("background: transparent; color: #cdd6f4; font-weight: 500; font-size: 14px;")
            message_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            
            # Enable HTML rendering for markdown
            message_label.setTextFormat(Qt.TextFormat.RichText)
            
            # Set font
            font = QFont("Segoe UI", 10)
            font.setWeight(QFont.Weight.Normal)
            message_label.setFont(font)
            
            # Process markdown for user messages using the styler
            processed_text = MarkdownStyler.process_markdown(text)
            message_label.setText(processed_text)
            
            # Simple layout for the bubble
            bubble_layout = QVBoxLayout(bubble_frame)
            bubble_layout.setContentsMargins(0, 0, 0, 0)
            bubble_layout.addWidget(message_label)
            
            container_layout.addWidget(bubble_frame, 2)  # Takes 2/3 of remaining space
            
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
                }
            """)
            
            # Create the message label
            message_label = QLabel()
            message_label.setWordWrap(True)
            message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            message_label.setStyleSheet("background: transparent; color: #cdd6f4; font-size: 14px;")
            message_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            
            # Enable HTML rendering for markdown
            message_label.setTextFormat(Qt.TextFormat.RichText)
            
            # Set font
            font = QFont("Segoe UI", 10)
            message_label.setFont(font)
            
            # Process markdown for assistant messages using the styler
            processed_text = MarkdownStyler.process_markdown(text)
            message_label.setText(processed_text)
            
            # Simple layout for the bubble
            bubble_layout = QVBoxLayout(bubble_frame)
            bubble_layout.setContentsMargins(0, 0, 0, 0)
            bubble_layout.addWidget(message_label)
            
            container_layout.addWidget(bubble_frame, 2)  # Takes 2/3 of space
            container_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))


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
    
    def _add_message_widget(self, widget: QWidget):
        """Helper method to add a message widget with proper stretch handling."""
        # Remove the stretch temporarily
        self.messages_layout.takeAt(self.messages_layout.count() - 1)
        
        # Add the message widget
        self.messages_layout.addWidget(widget)
        
        # Add stretch back
        self.messages_layout.addStretch()
        
        # Scroll to bottom
        self.scroll_to_bottom()
    
    def add_user_message(self, text: str):
        """Add user message."""
        bubble = MessageBubble(text, is_user=True)
        self._add_message_widget(bubble)
    
    def add_assistant_message(self, text: str):
        """Add assistant message."""
        bubble = MessageBubble(text, is_user=False)
        self._add_message_widget(bubble)
    
    def clear_chat(self):
        """Clear all messages."""
        # Remove all widgets except the stretch
        while self.messages_layout.count() > 1:
            child = self.messages_layout.takeAt(0)
            if child and child.widget():
                widget = child.widget()
                if widget:
                    widget.deleteLater()
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the chat."""
        # Force update the layout
        self.messages_widget.updateGeometry()
        # Scroll to bottom after a brief delay to ensure layout is updated
        scrollbar = self.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())
