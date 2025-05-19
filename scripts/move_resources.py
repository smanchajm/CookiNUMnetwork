"""
Script pour déplacer les ressources vers le nouveau dossier resources.
"""

import os
import shutil
from pathlib import Path


def create_directory(path: Path) -> None:
    """Crée un répertoire s'il n'existe pas."""
    if not path.exists():
        path.mkdir(parents=True)


def move_resources() -> None:
    """Déplace les ressources vers le nouveau dossier resources."""
    # Chemins source
    src_assets = Path("src/ui/assets")
    src_styles = Path("src/ui/styles")

    # Chemins destination
    dst_resources = Path("resources")
    dst_icons = dst_resources / "icons"
    dst_images = dst_resources / "images"
    dst_fonts = dst_resources / "fonts"
    dst_styles = dst_resources / "styles"

    # Création des répertoires de destination
    for directory in [dst_resources, dst_icons, dst_images, dst_fonts, dst_styles]:
        create_directory(directory)

    # Déplacement des ressources
    if src_assets.exists():
        # Déplacement des icônes
        src_icons = src_assets / "icons"
        if src_icons.exists():
            for item in src_icons.iterdir():
                if item.is_file():
                    shutil.copy2(item, dst_icons / item.name)

        # Déplacement des images
        src_images = src_assets / "images"
        if src_images.exists():
            for item in src_images.iterdir():
                if item.is_file():
                    shutil.copy2(item, dst_images / item.name)

        # Déplacement des polices
        src_fonts = src_assets / "fonts"
        if src_fonts.exists():
            for item in src_fonts.iterdir():
                if item.is_file():
                    shutil.copy2(item, dst_fonts / item.name)

    # Déplacement des styles
    if src_styles.exists():
        for item in src_styles.iterdir():
            if item.is_file():
                shutil.copy2(item, dst_styles / item.name)

    print("Ressources déplacées avec succès !")


if __name__ == "__main__":
    move_resources()
