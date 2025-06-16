from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QPushButton,
)

from src.core.camera_connection.gopro_service import GoProService
from src.ui.widgets.action_button import ActionButton


class WiFiConnectionDialog(QDialog):
    """
    Dialogue pour la génération d'un QR code de connexion WiFi pour GoPro.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration WiFi GoPro")
        self.setModal(True)
        self.gopro_service = GoProService()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Message d'information
        self.title_label = QLabel("Configuration WiFi pour GoPro")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Formulaire pour SSID et mot de passe
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)

        self.ssid_input = QLineEdit()

        # Création d'un widget horizontal pour le champ de mot de passe et le bouton
        password_widget = QWidget()
        password_layout = QHBoxLayout(password_widget)
        password_layout.setContentsMargins(0, 0, 0, 0)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.toggle_password_button = QPushButton()
        self.toggle_password_button.setFixedWidth(30)
        self.toggle_password_button.setCheckable(True)
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)
        self.toggle_password_button.setText("👁")

        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_password_button)

        form_layout.addRow("Nom du réseau (SSID):", self.ssid_input)
        form_layout.addRow("Mot de passe:", password_widget)
        layout.addWidget(form_widget)

        # Bouton pour générer le QR code
        self.generate_button = ActionButton("Générer QR Code")
        self.generate_button.clicked.connect(self.generate_qrcode)
        layout.addWidget(self.generate_button)

        # Label pour afficher le QR code
        self.status_label = QLabel(
            "Entrez les informations WiFi et cliquez sur Générer"
        )
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.qrcode_label = QLabel()
        self.qrcode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qrcode_label.setMinimumSize(200, 200)
        layout.addWidget(self.qrcode_label)

        # Instructions d'utilisation
        self.instruction_label = QLabel(
            "Une fois le QR code généré, scannez-le avec votre GoPro pour qu'elle se connecte automatiquement au réseau WiFi."
        )
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.instruction_label)

        # Bouton pour fermer
        self.close_button = ActionButton("Fermer", css_class="secondary_button")
        self.close_button.clicked.connect(self.on_close_clicked)
        layout.addWidget(self.close_button)

    def generate_qrcode(self):
        ssid = self.ssid_input.text().strip()
        password = self.password_input.text()

        if not ssid:
            self.status_label.setText("Veuillez entrer un nom de réseau (SSID)")
            return

        qrcode_file = self.gopro_service.generate_wifi_qrcode(ssid, password)

        # Afficher le QR code généré
        if Path(qrcode_file).exists():
            pixmap = QPixmap(str(qrcode_file))
            self.qrcode_label.setPixmap(
                pixmap.scaled(
                    self.qrcode_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            self.status_label.setText(f"QR code généré pour le réseau {ssid}")
            self.instruction_label.setText(
                "Scannez ce QR code avec votre GoPro pour la connecter au réseau WiFi."
            )

    def on_close_clicked(self):
        self.reject()

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_button.setText("🔒")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_button.setText("👁")
