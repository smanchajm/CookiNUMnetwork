import ctypes
import sys
import os
import locale

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from src.core.logging_config import logger
from src.core.main_controller import MainController
from src.ui.styles.style_manager import StyleManager
from src.ui.views.main_window import MainWindow
from src.utils.fonts import add_fonts
from src.utils.resource_manager import ResourceManager


# Forcer l'encodage UTF-8
def configure_encoding():
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.stderr.encoding != "utf-8":
        sys.stderr.reconfigure(encoding="utf-8")

    # Forcer la locale
    try:
        locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, "French_France.UTF-8")
        except locale.Error:
            logger.warning("Warning: Impossible de définir la locale française")

    # Forcer l'encodage des variables d'environnement
    os.environ["PYTHONIOENCODING"] = "utf-8"


def main():
    configure_encoding()
    app = QApplication([])
    app.setApplicationName("CookinNUMnetwork")

    # Configure font antialiasing
    font = QFont()
    font.setPixelSize(12)
    app.setFont(font)
    add_fonts()

    if sys.platform == "win32":
        # This line is essential for the icon to appear in the taskbar
        appID = "UPEC.CookinNUMnetwork.0.1"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID)

    # Load styles via StyleManager
    styles = StyleManager.load_styles()
    app.setStyleSheet(app.styleSheet() + styles)

    # Create the main window and the controller
    ResourceManager.create_app_data_paths()
    logger.info(ResourceManager.get_ipv4_address())
    window = MainWindow()
    MainController(window)

    window.showMaximized()
    window.activateWindow()
    logger.info("Application started successfully")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
