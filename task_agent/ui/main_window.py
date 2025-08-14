from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QListWidget, QPushButton, QListWidgetItem
from .task_widget_item import TaskWidgetItem
from .add_task_dialog import AddTaskDialog

class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Task Manager")
        self.resize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.task_list = QListWidget()
        layout.addWidget(self.task_list)

        self.add_task_button = QPushButton("Add Task")
        self.add_task_button.clicked.connect(self.show_add_task_dialog)
        layout.addWidget(self.add_task_button)

        self.load_tasks()

    def load_tasks(self):
        self.task_list.clear()
        tasks = self.db_manager.get_all_tasks()
        for task_id, description, frequency in tasks:
            item = QListWidgetItem(self.task_list)
            widget = TaskWidgetItem(task_id, description, frequency)
            widget.taskDeleted.connect(self.delete_task)
            item.setSizeHint(widget.sizeHint())
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, widget)

    def show_add_task_dialog(self):
        dialog = AddTaskDialog(self)
        if dialog.exec():
            task_data = dialog.get_task_data()
            self.db_manager.add_task(
                task_data["description"], task_data["frequency"]
            )
            self.load_tasks()

    def delete_task(self, task_id):
        self.db_manager.delete_task(task_id)
        self.load_tasks()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
