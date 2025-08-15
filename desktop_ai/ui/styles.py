"""UI styles for the application."""

# Application stylesheet
STYLESHEET = """
QMainWindow { 
    background-color: #1e1e2e; 
    color: #cdd6f4;
}

QTextEdit { 
    background-color: #181825; 
    color: #cdd6f4; 
    border: 2px solid #313244; 
    border-radius: 12px; 
    font-size: 14px; 
    padding: 12px; 
    font-family: 'Segoe UI', 'SF Pro Display', system-ui, sans-serif;
}

QLineEdit { 
    background-color: #181825; 
    color: #cdd6f4; 
    border: 2px solid #313244; 
    border-radius: 8px; 
    padding: 12px 16px; 
    font-size: 14px; 
    font-family: 'Segoe UI', 'SF Pro Display', system-ui, sans-serif;
}

QLineEdit:focus {
    border: 2px solid #89b4fa;
    background-color: #1e1e2e;
}

QLineEdit::placeholder {
    color: #6c7086;
    font-style: italic;
}

QPushButton { 
    background-color: #313244; 
    color: #cdd6f4; 
    border: 2px solid #45475a; 
    border-radius: 8px; 
    padding: 10px 20px; 
    font-size: 13px; 
    font-weight: 600; 
    font-family: 'Segoe UI', 'SF Pro Display', system-ui, sans-serif;
    min-height: 16px;
}

QPushButton:hover { 
    background-color: #45475a; 
    border: 2px solid #585b70;
}

QPushButton:pressed { 
    background-color: #585b70; 
    border: 2px solid #6c7086;
}

/* Special button styles */
QPushButton#refreshButton {
    background-color: #45475a;
    color: #cdd6f4;
    border: 2px solid #585b70;
    font-weight: bold;
}

QPushButton#refreshButton:hover {
    background-color: #585b70;
    border: 2px solid #6c7086;
}

QPushButton#resetButton {
    background-color: #45475a;
    color: #cdd6f4;
    border: 2px solid #585b70;
    font-weight: bold;
}

QPushButton#resetButton:hover {
    background-color: #585b70;
    border: 2px solid #6c7086;
}

QPushButton#historyButton {
    background-color: #45475a;
    color: #cdd6f4;
    border: 2px solid #585b70;
    font-weight: bold;
}

QPushButton#historyButton:hover {
    background-color: #585b70;
    border: 2px solid #6c7086;
}

/* Send button special style */
QPushButton#sendButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: 2px solid #89b4fa;
    font-weight: bold;
    min-width: 80px;
    padding: 12px 24px;
}

QPushButton#sendButton:hover {
    background-color: #74c7ec;
    border: 2px solid #74c7ec;
}

QPushButton#sendButton:pressed {
    background-color: #89dceb;
    border: 2px solid #89dceb;
}

QComboBox { 
    background-color: #181825; 
    color: #cdd6f4; 
    border: 2px solid #313244; 
    border-radius: 8px; 
    padding: 8px 12px; 
    font-size: 14px; 
    min-width: 200px; 
    font-family: 'Segoe UI', 'SF Pro Display', system-ui, sans-serif;
}

QComboBox:focus {
    border: 2px solid #89b4fa;
}

QComboBox::drop-down { 
    border: none; 
    width: 30px;
    background-color: #313244;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
}

QComboBox::down-arrow { 
    image: none; 
    border: none; 
    width: 12px;
    height: 12px;
    background-color: #89b4fa;
}

QComboBox QAbstractItemView { 
    background-color: #181825; 
    color: #cdd6f4; 
    border: 2px solid #313244; 
    border-radius: 8px;
    selection-background-color: #89b4fa; 
    selection-color: #1e1e2e;
    padding: 4px;
}

QLabel { 
    color: #cdd6f4; 
    font-size: 14px; 
    font-weight: 600;
    font-family: 'Segoe UI', 'SF Pro Display', system-ui, sans-serif;
}

QScrollArea {
    background-color: #181825;
    border: none;
}

QScrollBar:vertical { 
    border: none; 
    background: #181825; 
    width: 14px; 
    border-radius: 7px;
}

QScrollBar::handle:vertical { 
    background: #45475a; 
    min-height: 20px; 
    border-radius: 7px; 
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background: #585b70;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { 
    height: 0px; 
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { 
    background: none; 
}

QListWidget {
    background-color: #181825;
    color: #cdd6f4;
    border: 2px solid #313244;
    border-radius: 12px;
    font-size: 14px;
    padding: 8px;
    font-family: 'Segoe UI', 'SF Pro Display', system-ui, sans-serif;
}

QListWidget::item {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 8px;
    margin: 2px;
    padding: 8px;
}

QListWidget::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}

QListWidget::item:hover {
    background-color: #313244;
}

QDialog {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

/* QMessageBox styling */
QMessageBox {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

QMessageBox QPushButton {
    background-color: #45475a;
    color: #cdd6f4;
    border: 2px solid #585b70;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
    font-family: 'Segoe UI', 'SF Pro Display', system-ui, sans-serif;
    min-height: 16px;
    min-width: 60px;
}

QMessageBox QPushButton:hover {
    background-color: #585b70;
    border: 2px solid #6c7086;
}

QMessageBox QPushButton:pressed {
    background-color: #6c7086;
    border: 2px solid #7f849c;
}
"""
