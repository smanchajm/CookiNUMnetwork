import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from src.ui.views.main_window import MainWindow
from src.core.main_controller import MainController
from src.utils.fonts import add_fonts
from src.ui.styles.style_manager import StyleManager
import ctypes


def main():
    app = QApplication([])
    app.setApplicationName("CookinNUMnetwork")

    # Configure font antialiasing
    font = QFont()
    font.setPixelSize(12)
    app.setFont(font)

    if sys.platform == "win32":
        # Cette ligne est essentielle pour que l'icône apparaisse dans la barre des tâches
        appID = "UPEC.CookinNUMnetwork.0.1"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID)

    add_fonts()

    # Chargement des styles via le StyleManager
    styles = StyleManager.load_styles()
    app.setStyleSheet(app.styleSheet() + styles)

    # Create the main window and the controller
    window = MainWindow()
    controller = MainController(window)

    window.showMaximized()
    app.setActiveWindow(window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
