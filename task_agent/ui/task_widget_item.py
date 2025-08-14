from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal

class TaskWidgetItem(QWidget):
    taskDeleted = pyqtSignal(int)

    def __init__(self, task_id, description, frequency):
        super().__init__()
        self.task_id = task_id

        layout = QHBoxLayout()
        layout.addWidget(QLabel(f"<b>{description}</b><br>{frequency}"))
        layout.addStretch()

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self._on_delete_clicked)
        layout.addWidget(delete_button)

        self.setLayout(layout)

    def _on_delete_clicked(self):
        self.taskDeleted.emit(self.task_id)
