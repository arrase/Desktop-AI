"""UI helper components and style constants.

Keeps `main_window` lean and focused on interactions.
"""
from __future__ import annotations

from textwrap import dedent
import html
import markdown2

APP_STYLESHEET = dedent(
    """
    QMainWindow { background-color: #2E3440; }
    QTextEdit { background-color: #3B4252; color: #ECEFF4; border: 1px solid #4C566A; border-radius: 5px; font-size: 14px; padding: 5px; }
    QLineEdit { background-color: #3B4252; color: #ECEFF4; border: 1px solid #4C566A; border-radius: 5px; padding: 8px; font-size: 14px; }
    QPushButton { background-color: #5E81AC; color: #ECEFF4; border: none; border-radius: 5px; padding: 8px 16px; font-size: 14px; font-weight: bold; }
    QPushButton:hover { background-color: #81A1C1; }
    QPushButton:pressed { background-color: #88C0D0; }
    QScrollBar:vertical { border: none; background: #3B4252; width: 12px; }
    QScrollBar::handle:vertical { background: #5E81AC; min-height: 20px; border-radius: 6px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
    """
).strip()


def render_user_message(user_text: str) -> str:
    safe_text = html.escape(user_text)
    return f"""
    <div style='text-align: right; margin-bottom: 10px;'>
      <div style='background-color: #5E81AC; color: #ECEFF4; display: inline-block; padding: 10px; border-radius: 8px; max-width: 70%; text-align: left;'>
        <b>You</b>
        <p style='margin:5px 0 0 0;'>{safe_text}</p>
      </div>
    </div>
    """.strip()


def render_assistant_message(markdown: str) -> str:
    
    html_response = markdown2.markdown(
        markdown, extras=["fenced-code-blocks", "tables"]
    )

    html_response = html_response.replace(
        '<code>',
        '<code style="background-color:#4C566A; border-radius:3px; padding:2px 4px; font-family:monospace;">'
    ).replace(
        '<pre>',
        '<pre style="background-color:#434C5E; border:1px solid #4C566A; border-radius:5px; padding:10px; white-space:pre-wrap; word-wrap:break-word;">'
    )
    return f"""
  <div style='text-align: left; margin-bottom: 10px;'>
    <div style='background-color: #434C5E; color: #D8DEE9; display: inline-block; padding: 10px; border-radius: 8px; max-width: 70%; text-align: left;'>
    <b>Assistant</b>
    <div style='margin:5px 0 0 0;'>{html_response}</div>
    </div>
  </div>
  """.strip()


__all__ = [
    "APP_STYLESHEET",
    "render_user_message",
    "render_assistant_message",
]
