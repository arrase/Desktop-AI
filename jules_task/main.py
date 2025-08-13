import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSystemTrayIcon,
    QMenu,
    QStyle,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QMessageBox,
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from .add_task_dialog import AddTaskDialog
from .database import DatabaseManager


class TaskWidgetItem(QWidget):
    def __init__(self, task_id, description, frequency, main_window):
        super().__init__()
        self.task_id = task_id
        self.main_window = main_window

        layout = QHBoxLayout()
        layout.addWidget(QLabel(f"<b>{description}</b><br>{frequency}"))
        layout.addStretch()

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_task)
        layout.addWidget(delete_button)

        self.setLayout(layout)

    def delete_task(self):
        self.main_window.delete_task(self.task_id)


class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Jules Task Manager")
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
        for task in tasks:
            task_id, description, frequency = task
            item = QListWidgetItem(self.task_list)
            widget = TaskWidgetItem(task_id, description, frequency, self)
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


class JulesTaskApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)

        self.db_manager = DatabaseManager()

        # Main Window
        self.main_window = MainWindow(self.db_manager)

        # System Tray Icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        )
        self.tray_icon.setToolTip("Jules Task Manager")
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # Tray Menu
        tray_menu = QMenu()
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tray_menu.addAction(settings_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.on_exit)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # Left click
            self.main_window.show()

    def show_settings(self):
        # This will be implemented in a future step
        QMessageBox.information(
            self.main_window,
            "Settings",
            "Settings dialog not implemented yet."
        )

    def on_exit(self):
        self.db_manager.close()
        self.quit()

    def run(self):
        self.main_window.show()
        sys.exit(self.exec())


def main():
    app = JulesTaskApp(sys.argv)
    app.run()


if __name__ == "__main__":
    main()
