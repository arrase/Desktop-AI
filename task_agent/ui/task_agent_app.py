from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QStyle, QMessageBox
from PyQt6.QtGui import QAction
from .main_window import MainWindow
from ..database import DatabaseManager
import sys

class TaskAgentApp(QApplication):
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
        self.tray_icon.setToolTip("Task Manager")
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
            self.main_window, "Settings", "Settings dialog not implemented yet."
        )

    def on_exit(self):
        self.quit()

    def run(self):
        self.main_window.show()
        sys.exit(self.exec())
