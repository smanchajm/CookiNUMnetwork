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


def main():
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
    window = MainWindow()
    MainController(window)

    window.showMaximized()
    window.activateWindow()
    logger.info("Application started successfully")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
