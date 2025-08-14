"""UI helper components and style constants.

Keeps `main_window` lean and focused on interactions.
Bubble styles are inline so the QTextEdit renderer (limited CSS) applies them reliably.
"""
from __future__ import annotations

from textwrap import dedent
import html
import markdown2

APP_STYLESHEET = dedent(
    """
    QMainWindow { background-color: #2E3440; }
    QTextEdit { background-color: #2E3440; color: #ECEFF4; border: 1px solid #4C566A; border-radius: 6px; font-size: 14px; padding: 8px; }
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

BUBBLE_STYLE = (
    "background:#3B4252; color:#E5E9F0; "
    "padding:10px 14px; max-width:70%; font-size:14px; line-height:1.4; "
    "border:1px solid #465064; box-shadow:0 2px 4px rgba(0,0,0,.35); "
    "font-family:'Segoe UI', sans-serif; border-radius:4px 16px 16px 16px;"
)

CONTENT_P_STYLE = "margin:0;"


def render_user_message(user_text: str) -> str:
    """Return HTML for a user message (right aligned bubble)."""
    safe_text = html.escape(user_text).replace("\n", "<br>")
    return (
        "<div style='text-align:right; margin:8px 0;'>"
        f"<div style='display:inline-block; vertical-align:top; {BUBBLE_STYLE}'>"
        f"<p style='{CONTENT_P_STYLE}'>{safe_text}</p>"
        "</div></div>"
    )


def render_assistant_message(markdown: str) -> str:
    """Convert assistant markdown to an HTML bubble (left aligned)."""
    html_response = markdown2.markdown(
        markdown, extras=["fenced-code-blocks", "tables"])
    html_response = html_response.replace(
        '<pre>',
        '<pre style="background:#434C5E; border:1px solid #4C566A; border-radius:8px; padding:10px; white-space:pre-wrap; word-wrap:break-word; font-family:monospace; font-size:13px; margin:6px 0 0 0;">'
    ).replace(
        '<code>',
        '<code style="background:#4C566A; border-radius:4px; padding:2px 4px; font-family:monospace; font-size:13px;">'
    )
    return (
        "<div style='text-align:left; margin:8px 0;'>"
        f"<div style='display:inline-block; vertical-align:top; {BUBBLE_STYLE}'>"
        f"<div>{html_response}</div>"
        "</div></div>"
    )


__all__ = [
    "APP_STYLESHEET",
    "BUBBLE_STYLE",
    "render_user_message",
    "render_assistant_message",
]
