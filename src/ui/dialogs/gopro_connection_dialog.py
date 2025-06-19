from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QVBoxLayout,
)

from src.core.camera_connection.gopro_service import GoProService
from src.ui.widgets.action_button import ActionButton
from src.utils.resource_manager import ResourceManager


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

        # Label pour afficher l'URL de streaming
        self.url_label = QLabel()
        self.url_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.url_label.setWordWrap(True)
        layout.addWidget(self.url_label)

        self.cancel_button = ActionButton("Fermer", css_class="secondary_button")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        layout.addWidget(self.cancel_button)

    def generate_qrcode(self):
        self.gopro_service.qrcode_gopro(ResourceManager.get_gopro_streaming_url())
        self.url_label.setText(f"URL: {ResourceManager.get_streaming_url()}")

        # Afficher le QR code généré
        qrcode_file = ResourceManager.get_app_data_paths("qrcode") / "gopro_qrcode.png"
        if qrcode_file.exists():
            pixmap = QPixmap(str(qrcode_file))
            self.qrcode_label.setPixmap(
                pixmap.scaled(
                    self.qrcode_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

    def on_cancel_clicked(self):
        self.reject()
