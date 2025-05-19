from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
)

from src.core.event_handler import events
from src.ui.utils.layouts import create_hbox_layout
from src.ui.views.sidebar import Sidebar
from src.ui.views.media_player import MediaPlayer
from src.utils.resource_manager import ResourceManager


class MainWindow(QMainWindow):
    """
    Main window of the CookiNUMnetwork application.
    This class handles the UI layout and is connected to the controller.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CookiNUMnetwork")
        self.setWindowIcon(QIcon(ResourceManager.get_icon_path("Logo-CookiNUM-v.svg")))

        self.setup_ui()

    def setup_ui(self):
        """Configure the main user interface."""
        central_widget = QWidget()

        self.sidebar = Sidebar()
        self.media_player = MediaPlayer()

        content_layout = create_hbox_layout(
            widgets=[self.sidebar, self.media_player], spacing=0
        )

        content_layout.setStretchFactor(self.sidebar, 2)
        content_layout.setStretchFactor(self.media_player, 15)

        central_widget.setLayout(content_layout)
        self.setCentralWidget(central_widget)

    def closeEvent(self, event):
        """
        Handle application close event.
        """
        events.application_closing.emit()
        event.accept()
