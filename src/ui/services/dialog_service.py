"""
Application dialog management service.
"""

from PyQt6.QtWidgets import QMessageBox

from src.ui.dialogs.gopro_connection_dialog import GoProConnectionDialog
from src.ui.dialogs.wifi_connection_dialog import WiFiConnectionDialog


class DialogService:
    """
    Application dialog manager.
    """

    def __init__(self, parent):
        self.parent = parent
        self.gopro_dialog = None
        self.wifi_dialog = None

    def show_gopro_dialog(self) -> None:
        """Display GoPro connection dialog."""
        if self.gopro_dialog is None:
            self.gopro_dialog = GoProConnectionDialog(self.parent)
        self.gopro_dialog.show()

    def show_wifi_dialog(self) -> None:
        """Display WiFi configuration dialog for GoPro."""
        if self.wifi_dialog is None:
            self.wifi_dialog = WiFiConnectionDialog(self.parent)
        self.wifi_dialog.show()

    def show_error_message(self, message: str) -> None:
        """Display an error message to the user."""
        QMessageBox.critical(self.parent, "Error", message)
