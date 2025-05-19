"""
Gestionnaire de ressources pour l'application.
Utilise importlib.resources pour accéder aux ressources de manière portable.
"""

import importlib.resources
import os
from pathlib import Path
from typing import Union


class ResourceManager:
    """Gestionnaire de ressources pour l'application."""

    @staticmethod
    def get_resource_path(resource_name: str) -> Path:
        """
        Obtient le chemin complet vers une ressource.

        Args:
            resource_name: Nom de la ressource (chemin relatif depuis le dossier resources)

        Returns:
            Path: Chemin complet vers la ressource
        """
        try:
            # Utilise importlib.resources pour obtenir le chemin de la ressource
            return importlib.resources.files("resources").joinpath(resource_name)
        except Exception as e:
            raise FileNotFoundError(f"Ressource non trouvée: {resource_name}") from e

    @staticmethod
    def get_resource_content(resource_name: str) -> str:
        """
        Lit le contenu d'une ressource texte.

        Args:
            resource_name: Nom de la ressource (chemin relatif depuis le dossier resources)

        Returns:
            str: Contenu de la ressource
        """
        try:
            return (
                importlib.resources.files("resources")
                .joinpath(resource_name)
                .read_text(encoding="utf-8")
            )
        except Exception as e:
            raise FileNotFoundError(f"Ressource non trouvée: {resource_name}") from e

    @staticmethod
    def get_resource_bytes(resource_name: str) -> bytes:
        """
        Lit le contenu binaire d'une ressource.

        Args:
            resource_name: Nom de la ressource (chemin relatif depuis le dossier resources)

        Returns:
            bytes: Contenu binaire de la ressource
        """
        try:
            return (
                importlib.resources.files("resources")
                .joinpath(resource_name)
                .read_bytes()
            )
        except Exception as e:
            raise FileNotFoundError(f"Ressource non trouvée: {resource_name}") from e

    @staticmethod
    def get_icon_path(icon_name: str) -> Path:
        """
        Obtient le chemin vers une icône.

        Args:
            icon_name: Nom de l'icône (avec extension)

        Returns:
            Path: Chemin complet vers l'icône
        """
        return str(ResourceManager.get_resource_path(f"icons/{icon_name}"))

    @staticmethod
    def get_image_path(image_name: str) -> Path:
        """
        Obtient le chemin vers une image.

        Args:
            image_name: Nom de l'image (avec extension)

        Returns:
            Path: Chemin complet vers l'image
        """
        return ResourceManager.get_resource_path(f"images/{image_name}")

    @staticmethod
    def get_font_path(font_name: str) -> Path:
        """
        Obtient le chemin vers une police.

        Args:
            font_name: Nom de la police (avec extension)

        Returns:
            Path: Chemin complet vers la police
        """
        return ResourceManager.get_resource_path(f"fonts/{font_name}")

    @staticmethod
    def get_style_content() -> str:
        """
        Obtient le contenu du fichier de style principal.

        Returns:
            str: Contenu du fichier de style
        """
        return ResourceManager.get_resource_content("styles/styles.qss")
