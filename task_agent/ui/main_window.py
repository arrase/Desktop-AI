from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from ..agent import ChatAgent
import asyncio

class AgentWorker(QObject):
    response_received = pyqtSignal(str)

    def __init__(self, agent, prompt):
        super().__init__()
        self.agent = agent
        self.prompt = prompt

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(self.agent.get_response(self.prompt))
        self.response_received.emit(response)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.agent = ChatAgent()
        self.setWindowTitle("Chatbot")
        self.resize(800, 600)

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

    def send_message(self):
        user_message = self.input_box.text().strip()
        if not user_message:
            return

        self.chat_history.append(f"<b>You:</b> {user_message}")
        self.input_box.clear()

        self.thread = QThread()
        self.worker = AgentWorker(self.agent, user_message)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.response_received.connect(self.handle_response)
        self.worker.response_received.connect(self.thread.quit)
        self.worker.response_received.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()
        self.send_button.setEnabled(False)
        self.input_box.setEnabled(False)

    def handle_response(self, response):
        self.chat_history.append(f"<b>Assistant:</b> {response}")
        self.send_button.setEnabled(True)
        self.input_box.setEnabled(True)
        self.input_box.setFocus()

    def closeEvent(self, event: QCloseEvent):
        self.hide()
        event.ignore()
