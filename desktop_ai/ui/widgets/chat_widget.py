"""Simple chat display widget."""
from typing import List
from PyQt6.QtWidgets import QTextEdit

from ..styles import render_user_message, render_assistant_message


class ChatWidget(QTextEdit):
    """Simple chat display widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self._messages: List[str] = []
        self._clear_display()
    
    def add_user_message(self, text: str):
        """Add user message."""
        self._messages.append(render_user_message(text))
        self._update_display()
    
    def add_assistant_message(self, text: str):
        """Add assistant message."""
        self._messages.append(render_assistant_message(text))
        self._update_display()
    
    def clear_chat(self):
        """Clear all messages."""
        self._messages.clear()
        self._clear_display()
    
    def _clear_display(self):
        """Clear the display."""
        self.setHtml("<html><body><div id='chat-root'></div></body></html>")
    
    def _update_display(self):
        """Update the display with all messages."""
        html_doc = (
            "<html><body><div id='chat-root'>" +
            "".join(self._messages) + 
            "</div></body></html>"
        )
        self.setHtml(html_doc)
        
        # Auto scroll to bottom
        scrollbar = self.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())
