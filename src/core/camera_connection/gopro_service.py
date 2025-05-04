import qrcode
import os
from PyQt6.QtCore import QObject

from src.core.event_handler import events
from src.core.constants import qrcode_path


class GoProService(QObject):
    """
    Service gérant la connexion et le contrôle des caméras GoPro.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_connected = False

    def connect(self):
        """
        Établit la connexion avec la GoPro.
        """
        try:
            # TODO: Implémenter la connexion à la GoPro
            self.is_connected = True
            events.connected.emit()
        except Exception as e:
            events.connection_error.emit(str(e))

    def qrcode_gopro(self, content: str):
        if not os.path.exists(qrcode_path):
            os.makedirs(qrcode_path)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)

        # Sauvegarder le QR code
        filename = os.path.join(qrcode_path, "gopro_qrcode.png")
        image = qr.make_image(fill_color="black", back_color="white")
        image.save(filename)

        events.qrcode_created.emit(f"QR code généré: {filename}")

    def generate_wifi_qrcode(self, ssid: str, password: str):
        """
        Génère un QR code pour la connexion WiFi avec le format spécial
        !MJOIN="SSID:PASSWORD" utilisé par les caméras GoPro.
        """
        if not os.path.exists(qrcode_path):
            os.makedirs(qrcode_path)

        # Format spécial pour les caméras GoPro
        content = f'!MJOIN="{ssid}:{password}"'

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)

        # Sauvegarder le QR code
        filename = os.path.join(qrcode_path, "wifi_qrcode.png")
        image = qr.make_image(fill_color="black", back_color="white")
        image.save(filename)

        events.qrcode_created.emit(f"QR code WiFi généré: {filename}")
        return filename

    def disconnect(self):
        """
        Déconnecte la GoPro.
        """
        try:
            # TODO: Implémenter la déconnexion de la GoPro
            self.is_connected = False
            events.disconnected.emit()
        except Exception as e:
            events.connection_error.emit(str(e))
