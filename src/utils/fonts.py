from PySide6.QtGui import QFontDatabase
from src.utils.resource_manager import ResourceManager
from src.core.logging_config import logger


def add_fonts():
    """Add fonts to the application."""
    font_dirs = ["roboto", "geist"]

    for font_dir in font_dirs:
        try:
            # Use ResourceManager to get font paths
            font_path = ResourceManager.get_font_path(font_dir)
            if font_path.exists():
                for font_file in font_path.glob("*.ttf"):
                    try:
                        QFontDatabase.addApplicationFont(str(font_file))
                    except Exception as e:
                        logger.error(f"Error loading font {font_file}: {e}")
        except Exception as e:
            logger.error(f"Error accessing font directory {font_dir}: {e}")
