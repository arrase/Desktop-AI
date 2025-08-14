"""Main application chat window."""
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
)
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtCore import QThread, pyqtSignal, QObject
import asyncio

from ..agent import ChatAgent  # type: ignore
from .components import (  # type: ignore
    APP_STYLESHEET,
    render_user_message,
    render_assistant_message,
)


class AgentWorker(QObject):
    """Worker that executes the agent's asynchronous request in a separate thread."""

    response_received = pyqtSignal(str)

    def __init__(self, agent: ChatAgent, prompt: str):
        super().__init__()
        self.agent = agent
        self.prompt = prompt

    def run(self):  # executes within the thread
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(self.agent.get_response(self.prompt))
        finally:
            loop.close()
        self.response_received.emit(response)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.agent = ChatAgent()
        self.setWindowTitle("Chatbot")
        self.resize(800, 600)
        self.setStyleSheet(APP_STYLESHEET)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        layout.addWidget(self.chat_history)

        self.input_box = QLineEdit()
        self.input_box.returnPressed.connect(self.send_message)
        layout.addWidget(self.input_box)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        # Internal references to thread / worker
        self._thread: QThread | None = None
        self._worker: AgentWorker | None = None

    # ---------------- Helpers internos ----------------
    def _thread_active(self) -> bool:
        if self._thread is None:
            return False
        try:
            return self._thread.isRunning()
        except RuntimeError:
            self._thread = None
            return False

    def _cleanup_thread(self):  # Qt slot for cleaning up thread references
        self._thread = None
        self._worker = None

    # ---------------- Acciones UI ----------------
    def send_message(self):
        user_message = self.input_box.text().strip()
        if not user_message:
            return

        self.chat_history.append(render_user_message(user_message))
        self.input_box.clear()

        # Evitar solapamiento (se podría implementar cola en futuro)
        if self._thread_active():
            return

        self._thread = QThread()
        self._worker = AgentWorker(self.agent, user_message)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.response_received.connect(self.handle_response)
        self._worker.response_received.connect(self._thread.quit)
        self._worker.response_received.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._cleanup_thread)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()
        self.send_button.setEnabled(False)
        self.input_box.setEnabled(False)

    def handle_response(self, response: str):
        self.chat_history.append(render_assistant_message(response))
        self.send_button.setEnabled(True)
        self.input_box.setEnabled(True)
        self.input_box.setFocus()

    # ---------------- Eventos ----------------
    def closeEvent(self, event: QCloseEvent):  # type: ignore[override]
        self.hide()
        event.ignore()
