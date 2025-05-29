"""
Gestionnaire de styles pour l'application.
"""

from src.core.logging_config import logger
from src.utils.resource_manager import ResourceManager


class StyleManager:
    """Gestionnaire de styles pour l'application."""

    @staticmethod
    def load_styles() -> str:
        """
        Charge les styles de l'application.

        Returns:
            str: Contenu du fichier de style
        """
        try:
            return ResourceManager.get_style_content()
        except FileNotFoundError:
            logger.warning("Attention: Fichier de style non trouvé")
            return ""
