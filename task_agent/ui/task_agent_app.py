from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QStyle, QMessageBox
from PyQt6.QtGui import QAction
from .main_window import MainWindow
import sys

class TaskAgentApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)

        # Main Window
        self.main_window = MainWindow()

        # System Tray Icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        )
        self.tray_icon.setToolTip("Chatbot")
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # Tray Menu
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_main_window)
        tray_menu.addAction(show_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.on_exit)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def show_main_window(self):
        self.main_window.showNormal()
        self.main_window.activateWindow()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # Left click
            self.show_main_window()

    def on_exit(self):
        self.quit()

    def run(self):
        self.main_window.show()
        sys.exit(self.exec())