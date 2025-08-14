from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from ..agent import ChatAgent
import asyncio
import markdown2


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

        self.setStyleSheet(self._create_stylesheet())

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

    def _create_stylesheet(self):
        return """
            QMainWindow {
                background-color: #2E3440;
            }
            QTextEdit {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                border-radius: 5px;
                font-size: 14px;
                padding: 5px;
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
            QPushButton:hover {
                background-color: #81A1C1;
            }
            QPushButton:pressed {
                background-color: #88C0D0;
            }
            QScrollBar:vertical {
                border: none;
                background: #3B4252;
                width: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #5E81AC;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """

    def send_message(self):
        user_message = self.input_box.text().strip()
        if not user_message:
            return

        user_html = f'''
        <div style="text-align: right; margin-bottom: 10px;">
            <div style="background-color: #5E81AC; color: #ECEFF4; display: inline-block; padding: 10px; border-radius: 8px; max-width: 70%; text-align: left;">
                <b>You</b>
                <p style="margin: 5px 0 0 0;">{user_message.replace('<', '&lt;').replace('>', '&gt;')}</p>
            </div>
        </div>
        '''
        self.chat_history.append(user_html)
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
        html_response = markdown2.markdown(response, extras=["fenced-code-blocks", "tables"])

        html_response = html_response.replace('<code>', '<code style="background-color: #4C566A; border-radius: 3px; padding: 2px 4px; font-family: monospace;">')
        html_response = html_response.replace('<pre>', '<pre style="background-color: #434C5E; border: 1px solid #4C566A; border-radius: 5px; padding: 10px; white-space: pre-wrap; word-wrap: break-word;">')

        assistant_html = f'''
        <div style="text-align: left; margin-bottom: 10px;">
            <div style="background-color: #434C5E; color: #D8DEE9; display: inline-block; padding: 10px; border-radius: 8px; max-width: 70%; text-align: left;">
                <b>Assistant</b>
                <div style="margin: 5px 0 0 0;">{html_response}</div>
            </div>
        </div>
        '''
        self.chat_history.append(assistant_html)
        self.send_button.setEnabled(True)
        self.input_box.setEnabled(True)
        self.input_box.setFocus()

    def closeEvent(self, event: QCloseEvent):
        self.hide()
        event.ignore()
