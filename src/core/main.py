import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from src.ui.views.main_window import MainWindow
from src.utils.fonts import add_fonts
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
    with open("src/ui/styles/styles.qss", "r") as style:
        app.setStyleSheet(app.styleSheet() + style.read())

    window = MainWindow()
    window.showMaximized()
    app.setActiveWindow(window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
