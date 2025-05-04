import os

from PyQt6.QtGui import QFontDatabase

from src.core.constants import fonts_path


def add_fonts():
    print(fonts_path)

    for font_dir in ["roboto", "geist"]:
        for font in filter(
            lambda s: s.endswith(".ttf"),
            os.listdir(os.path.join(fonts_path, font_dir)),
        ):
            try:
                QFontDatabase.addApplicationFont(
                    os.path.join(fonts_path, font_dir, font)
                )
            except:
                QFontDatabase.add_application_font(
                    os.path.join(fonts_path, font_dir, font)
                )
