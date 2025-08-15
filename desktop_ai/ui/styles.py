"""UI styles and message rendering."""
import html
import markdown2

# Application stylesheet
STYLESHEET = """
QMainWindow { background-color: #2E3440; }
QTextEdit { 
    background-color: #2E3440; 
    color: #ECEFF4; 
    border: 1px solid #4C566A; 
    border-radius: 6px; 
    font-size: 14px; 
    padding: 8px; 
}
QLineEdit { 
    background-color: #3B4252; 
    color: #ECEFF4; 
    border: 1px solid #4C566A; 
    border-radius: 5px; 
    padding: 8px; 
    font-size: 14px; 
}
QPushButton { 
    background-color: #5E81AC; 
    color: #ECEFF4; 
    border: none; 
    border-radius: 5px; 
    padding: 8px 16px; 
    font-size: 14px; 
    font-weight: bold; 
}
QPushButton:hover { background-color: #81A1C1; }
QPushButton:pressed { background-color: #88C0D0; }
QComboBox { 
    background-color: #3B4252; 
    color: #ECEFF4; 
    border: 1px solid #4C566A; 
    border-radius: 5px; 
    padding: 6px 8px; 
    font-size: 14px; 
    min-width: 200px; 
}
QComboBox::drop-down { border: none; }
QComboBox::down-arrow { image: none; border: none; }
QComboBox QAbstractItemView { 
    background-color: #3B4252; 
    color: #ECEFF4; 
    border: 1px solid #4C566A; 
    selection-background-color: #5E81AC; 
}
QLabel { color: #ECEFF4; font-size: 14px; font-weight: bold; }
QScrollBar:vertical { border: none; background: #3B4252; width: 12px; }
QScrollBar::handle:vertical { background: #5E81AC; min-height: 20px; border-radius: 6px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
QListWidget {
    background-color: #2E3440;
    color: #ECEFF4;
    border: 1px solid #4C566A;
    border-radius: 6px;
    font-size: 14px;
    padding: 4px;
}
QListWidget::item {
    background-color: #3B4252;
    border: 1px solid #4C566A;
    border-radius: 4px;
    margin: 2px;
    padding: 4px;
}
QListWidget::item:selected {
    background-color: #5E81AC;
}
QDialog {
    background-color: #2E3440;
}
"""

# Message bubble styles
BUBBLE_STYLE = (
    "background:#3B4252; color:#E5E9F0; "
    "padding:10px 14px; max-width:70%; font-size:14px; line-height:1.4; "
    "border:1px solid #465064; box-shadow:0 2px 4px rgba(0,0,0,.35); "
    "font-family:'Segoe UI', sans-serif; border-radius:4px 16px 16px 16px;"
)


def render_user_message(text: str) -> str:
    """Render user message bubble."""
    safe_text = html.escape(text).replace("\n", "<br>")
    return (
        "<div style='text-align:right; margin:8px 0;'>"
        f"<div style='display:inline-block; vertical-align:top; {BUBBLE_STYLE}'>"
        f"<p style='margin:0;'>{safe_text}</p>"
        "</div></div>"
    )


def render_assistant_message(markdown_text: str) -> str:
    """Render assistant message bubble with markdown support."""
    html_content = markdown2.markdown(
        markdown_text, extras=["fenced-code-blocks", "tables"]
    )
    
    # Style code blocks
    html_content = html_content.replace(
        '<pre>',
        '<pre style="background:#434C5E; border:1px solid #4C566A; '
        'border-radius:8px; padding:10px; white-space:pre-wrap; '
        'word-wrap:break-word; font-family:monospace; font-size:13px; margin:6px 0 0 0;">'
    ).replace(
        '<code>',
        '<code style="background:#4C566A; border-radius:4px; padding:2px 4px; '
        'font-family:monospace; font-size:13px;">'
    )
    
    return (
        "<div style='text-align:left; margin:8px 0;'>"
        f"<div style='display:inline-block; vertical-align:top; {BUBBLE_STYLE}'>"
        f"<div>{html_content}</div>"
        "</div></div>"
    )
