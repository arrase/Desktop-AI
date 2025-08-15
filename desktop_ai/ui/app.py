"""Main application class."""
import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QStyle
from PyQt6.QtGui import QAction

from .windows import MainWindow, SettingsWindow


class DesktopAI:
    """Main application with system tray support."""

    def __init__(self, app: QApplication):
        self.app = app
        self.app.setQuitOnLastWindowClosed(False)

        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("System tray is not available on this system.")
            sys.exit(1)

        # Main window
        self.main_window = MainWindow()

        # System tray
        self._setup_system_tray()

    def _setup_system_tray(self):
        """Setup system tray icon and menu."""
        self.tray_icon = QSystemTrayIcon()

        # Set icon
        style = self.app.style()
        if style:
            icon = style.standardIcon(
                QStyle.StandardPixmap.SP_MessageBoxQuestion)
            self.tray_icon.setIcon(icon)

        self.tray_icon.setToolTip("Desktop AI")

        # Connect activation signal with error handling
        self.tray_icon.activated.connect(self._on_tray_activated)

        # Setup menu
        self._setup_tray_menu()

        # Show tray icon
        self.tray_icon.show()

    def _setup_tray_menu(self):
        """Setup system tray menu."""
        menu = QMenu(self.main_window)

        show_action = QAction("Show", self.main_window)
        show_action.triggered.connect(self._show_window)
        menu.addAction(show_action)

        settings_action = QAction("Settings", self.main_window)
        settings_action.triggered.connect(self._show_settings)
        menu.addAction(settings_action)

        menu.addSeparator()

        exit_action = QAction("Exit", self.main_window)
        exit_action.triggered.connect(self.app.quit)
        menu.addAction(exit_action)

        self.tray_icon.setContextMenu(menu)

    def _show_window(self):
        """Show main window."""
        self.main_window.showNormal()
        self.main_window.activateWindow()

    def _show_settings(self):
        """Show settings window."""
        dialog = SettingsWindow(
            agent=self.main_window.agent,
            parent=self.main_window
        )
        dialog.exec()

    def _on_tray_activated(self, reason):
        """Handle tray icon activation."""
        try:
            if reason == QSystemTrayIcon.ActivationReason.Trigger:
                if self.main_window.isVisible():
                    self.main_window.hide()
                else:
                    self._show_window()
        except Exception as e:
            # Fallback: just show window on any activation
            if self.main_window.isVisible():
                self.main_window.hide()
            else:
                self._show_window()

    def run(self):
        """Run the application."""
        # Start hidden by default since we're running as daemon
        self.main_window.hide()

        # Execute the Qt event loop
        return self.app.exec()
