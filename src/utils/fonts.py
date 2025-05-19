from PyQt6.QtGui import QFontDatabase
from src.utils.resource_manager import ResourceManager


def add_fonts():
    """Ajoute les polices de caractères à l'application."""
    font_dirs = ["roboto", "geist"]

    for font_dir in font_dirs:
        try:
            # Utilise le ResourceManager pour obtenir le chemin des polices
            font_path = ResourceManager.get_font_path(font_dir)
            if font_path.exists():
                for font_file in font_path.glob("*.ttf"):
                    try:
                        QFontDatabase.addApplicationFont(str(font_file))
                    except Exception as e:
                        print(
                            f"Erreur lors du chargement de la police {font_file}: {e}"
                        )
        except Exception as e:
            print(f"Erreur lors de l'accès au dossier de polices {font_dir}: {e}")
