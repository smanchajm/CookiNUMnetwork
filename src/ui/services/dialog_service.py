"""
Service de gestion des dialogues de l'application.
"""

from PyQt6.QtWidgets import QMessageBox

from src.ui.dialogs.gopro_connection_dialog import GoProConnectionDialog
from src.ui.dialogs.wifi_connection_dialog import WiFiConnectionDialog


class DialogService:
    """
    Gestionnaire des dialogues de l'application.
    """

    def __init__(self, parent):
        self.parent = parent
        self.gopro_dialog = None
        self.wifi_dialog = None

    def show_gopro_dialog(self) -> None:
        """Affiche le dialogue de connexion GoPro."""
        if self.gopro_dialog is None:
            self.gopro_dialog = GoProConnectionDialog(self.parent)
        self.gopro_dialog.show()

    def show_wifi_dialog(self) -> None:
        """Affiche le dialogue de configuration WiFi pour GoPro."""
        if self.wifi_dialog is None:
            self.wifi_dialog = WiFiConnectionDialog(self.parent)
        self.wifi_dialog.show()

    def show_error_message(self, message: str) -> None:
        """Affiche un message d'erreur à l'utilisateur."""
        QMessageBox.critical(self.parent, "Erreur", message)
