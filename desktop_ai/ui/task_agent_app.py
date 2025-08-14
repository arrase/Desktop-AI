from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QStyle
from PyQt6.QtGui import QAction
from .main_window import MainWindow
import sys


class TaskAgentApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)

        # Main Window (create but do not show)
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
        # Toggle main window visibility on left click
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # Left click
            if self.main_window.isVisible():
                self.main_window.hide()
            else:
                self.show_main_window()

    def on_exit(self):
        self.quit()

    def run(self):
        # Start minimized to the system tray (do not show main window now)
        # The tray icon is already shown in __init__
        sys.exit(self.exec())
