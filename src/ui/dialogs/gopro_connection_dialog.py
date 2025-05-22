import os

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from src.ui.widgets.action_button import ActionButton
from src.core.camera_connection.gopro_service import GoProService
from src.core.constants import qrcode_path, streaming_rtmp_url_gopro


class GoProConnectionDialog(QDialog):
    """
    Dialogue pour la connexion à une caméra GoPro.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connexion GoPro")
        self.setModal(True)
        self.gopro_service = GoProService()
        self.setup_ui()
        self.generate_qrcode()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Message d'information
        self.status_label = QLabel("Scannez moi avec la caméra !")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Label pour afficher le QR code
        self.qrcode_label = QLabel()
        self.qrcode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qrcode_label.setMinimumSize(150, 150)
        layout.addWidget(self.qrcode_label)

        self.cancel_button = ActionButton("Fermer", css_class="secondary_button")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        layout.addWidget(self.cancel_button)

    def generate_qrcode(self):
        # Pour l'instant, on utilise un placeholder
        placeholder_content = "https://gopro.com/connect"
        self.gopro_service.qrcode_gopro(streaming_rtmp_url_gopro)

        # Afficher le QR code généré
        qrcode_file = os.path.join(qrcode_path, "gopro_qrcode.png")
        if os.path.exists(qrcode_file):
            pixmap = QPixmap(qrcode_file)
            self.qrcode_label.setPixmap(
                pixmap.scaled(
                    self.qrcode_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

    def on_cancel_clicked(self):
        self.reject()
