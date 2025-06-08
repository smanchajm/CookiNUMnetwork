"""
Gestionnaire de ressources pour l'application.
Utilise pathlib pour une gestion des chemins cross-platform.
Gère à la fois le mode développement et le mode PyInstaller.
"""

import importlib.resources
import os
import socket
import sys
from pathlib import Path
from typing import Union, Tuple


class ResourceManager:
    """Gestionnaire de ressources pour l'application."""

    APP_NAME = "CookiNUM"

    # Streaming configuration
    STREAMING_HOST = "localhost"
    STREAMING_RTMP_PORT = 1935
    STREAMING_RTSP_PORT = 8554
    STREAMING_PATH = "live/stream"

    @staticmethod
    def _get_streaming_url(protocol: str, port: int) -> str:
        """
        Construit une URL de streaming avec le protocole et le port spécifiés.

        Args:
            protocol: Protocole de streaming (rtmp ou rtsp)
            port: Port du serveur de streaming

        Returns:
            str: URL de streaming complète
        """
        return f"{protocol}://{ResourceManager.STREAMING_HOST}:{port}/{ResourceManager.STREAMING_PATH}"

    @staticmethod
    def _is_pyinstaller_mode() -> bool:
        """
        Vérifie si l'application est exécutée en mode PyInstaller.

        Returns:
            bool: True si en mode PyInstaller, False sinon
        """
        return getattr(sys, "frozen", False)

    @staticmethod
    def _get_base_path() -> Path:
        """
        Obtient le chemin de base pour les ressources.
        Gère à la fois le mode développement et le mode PyInstaller.

        Returns:
            Path: Chemin de base pour les ressources
        """
        if ResourceManager._is_pyinstaller_mode():
            # Mode PyInstaller: utilise le dossier temporaire créé par PyInstaller
            return Path(sys._MEIPASS)
        else:
            # Mode développement: utilise le dossier racine du projet
            return Path(__file__).parent.parent.parent

    @staticmethod
    def get_user_data_dir() -> Path:
        """
        Obtient le répertoire de données utilisateur approprié selon le système d'exploitation.
        Windows: %LOCALAPPDATA%/CookiNUM
        macOS: ~/Library/Application Support/CookiNUM
        Linux: ~/.cookinum

        Returns:
            Path: Chemin vers le répertoire de données utilisateur
        """
        if os.name == "nt":  # Windows
            local_appdata = os.getenv("LOCALAPPDATA") or (Path.home() / "AppData/Local")
            return Path(local_appdata) / ResourceManager.APP_NAME
        elif sys.platform == "darwin":  # macOS
            return (
                Path.home() / "Library/Application Support" / ResourceManager.APP_NAME
            )
        else:  # Linux
            return Path.home() / f".{ResourceManager.APP_NAME.lower()}"

    @staticmethod
    def create_app_data_paths() -> None:
        """
        Obtient les chemins des répertoires de données de l'application.
        Crée les répertoires s'ils n'existent pas.

        Returns:
            dict[str, Path]: Dictionnaire des chemins des sous-répertoires
        """
        app_data_path = ResourceManager.get_user_data_dir()
        app_data_path.mkdir(exist_ok=True)

        subdirs = {
            "videos": app_data_path / "videos",
            "tags": app_data_path / "tags",
            "qrcode": app_data_path / "qrcode",
        }

        for path in subdirs.values():
            path.mkdir(exist_ok=True)

    @staticmethod
    def get_app_data_paths(ressource_name: Union[str, Path]) -> Path:
        """
        Obtient le chemin complet vers une ressource dans le répertoire de données de l'application.

        Args:
            ressource_name: Nom de la ressource (chemin relatif depuis le dossier resources)

        Returns:
            Path: Chemin complet vers la ressource
        """
        return ResourceManager.get_user_data_dir() / ressource_name

    @staticmethod
    def get_ipv4_address() -> str:
        """
        Obtient l'adresse IPv4 de la machine.

        Returns:
            str: Adresse IPv4
        """
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)

    @staticmethod
    def get_gopro_rtmp_url() -> str:
        """
        Obtient l'URL de streaming RTMP pour GoPro.
        """
        return ResourceManager._get_streaming_url(
            "rtmp", ResourceManager.STREAMING_RTMP_PORT
        )

    @staticmethod
    def get_gopro_rtsp_url() -> str:
        """
        Obtient l'URL de streaming RTSP pour GoPro.
        """
        return ResourceManager._get_streaming_url(
            "rtsp", ResourceManager.STREAMING_RTSP_PORT
        )

    @staticmethod
    def get_gopro_streaming_url() -> str:
        """
        Obtient l'URL de streaming pour GoPro.

        Returns:
            str: URL de streaming GoPro
        """
        ip_address = ResourceManager.get_ipv4_address()
        return f'!MRTMP="rtmp://{ip_address}:{ResourceManager.STREAMING_RTMP_PORT}/{ResourceManager.STREAMING_PATH}"=oW1mVr1080!W!GL'

    @staticmethod
    def get_resource_path(resource_name: Union[str, Path]) -> Path:
        """
        Obtient le chemin complet vers une ressource.

        Args:
            resource_name: Nom de la ressource (chemin relatif depuis le dossier resources)
                          Peut être une chaîne ou un Path

        Returns:
            Path: Chemin complet vers la ressource
        """
        try:
            if ResourceManager._is_pyinstaller_mode():
                return (
                    ResourceManager._get_base_path()
                    / "src"
                    / "resources"
                    / resource_name
                )
            else:
                return Path(
                    importlib.resources.files("src.resources").joinpath(
                        str(resource_name)
                    )
                )
        except Exception as e:
            raise FileNotFoundError(f"Ressource non trouvée: {resource_name}") from e

    @staticmethod
    def get_resource_content(resource_name: Union[str, Path]) -> str:
        """
        Lit le contenu d'une ressource texte.

        Args:
            resource_name: Nom de la ressource (chemin relatif depuis le dossier resources)
                          Peut être une chaîne ou un Path

        Returns:
            str: Contenu de la ressource
        """
        try:
            resource_path = ResourceManager.get_resource_path(resource_name)
            return resource_path.read_text(encoding="utf-8")
        except Exception as e:
            raise FileNotFoundError(f"Ressource non trouvée: {resource_name}") from e

    @staticmethod
    def get_resource_bytes(resource_name: Union[str, Path]) -> bytes:
        """
        Lit le contenu binaire d'une ressource.

        Args:
            resource_name: Nom de la ressource (chemin relatif depuis le dossier resources)
                          Peut être une chaîne ou un Path

        Returns:
            bytes: Contenu binaire de la ressource
        """
        try:
            resource_path = ResourceManager.get_resource_path(resource_name)
            return resource_path.read_bytes()
        except Exception as e:
            raise FileNotFoundError(f"Ressource non trouvée: {resource_name}") from e

    @staticmethod
    def get_icon_path(icon_name: Union[str, Path]) -> Path:
        """
        Obtient le chemin vers une icône.

        Args:
            icon_name: Nom de l'icône (avec extension)

        Returns:
            Path: Chemin complet vers l'icône
        """
        return ResourceManager.get_resource_path(Path("icons") / icon_name)

    @staticmethod
    def get_image_path(image_name: Union[str, Path]) -> Path:
        """
        Obtient le chemin vers une image.

        Args:
            image_name: Nom de l'image (avec extension)

        Returns:
            Path: Chemin complet vers l'image
        """
        return ResourceManager.get_resource_path(Path("images") / image_name)

    @staticmethod
    def get_sound_path(sound_name: Union[str, Path]) -> Path:
        """
        Obtient le chemin vers un son.

        Args:
            sound_name: Nom du fichier son (avec extension)

        Returns:
            Path: Chemin complet vers le fichier son
        """
        return ResourceManager.get_resource_path(Path("sounds") / sound_name)

    @staticmethod
    def get_font_path(font_name: Union[str, Path]) -> Path:
        """
        Obtient le chemin vers une police.

        Args:
            font_name: Nom de la police (avec extension)

        Returns:
            Path: Chemin complet vers la police
        """
        return ResourceManager.get_resource_path(Path("fonts") / font_name)

    @staticmethod
    def get_font_dir(font_dir_name: Union[str, Path]) -> Path:
        """
        Obtient le chemin vers un dossier de polices.

        Args:
            font_dir_name: Nom du dossier de polices

        Returns:
            Path: Chemin complet vers le dossier de polices
        """
        return ResourceManager.get_resource_path(Path("fonts") / font_dir_name)

    @staticmethod
    def get_style_content() -> str:
        """
        Obtient le contenu du fichier de style principal.

        Returns:
            str: Contenu du fichier de style
        """
        return ResourceManager.get_resource_content(Path("styles") / "styles.qss")

    @staticmethod
    def get_mediamtx_args() -> Tuple[Path, Path]:
        """
        Obtient le chemin vers le binaire exécutable de MediaMTX en fonction du système d'exploitation.

        Returns:
            Tuple[Path, Path]: Tuple contenant le chemin vers le binaire et le fichier de configuration
        """
        binary_name = "mediamtx.exe" if sys.platform == "win32" else "mediamtx"
        return (
            ResourceManager.get_resource_path(Path("binaries/mediamtx") / binary_name),
            ResourceManager.get_resource_path(Path("binaries/mediamtx/mediamtx.yml")),
        )

    @staticmethod
    def get_audio_model_path() -> Path:
        """
        Obtient le chemin vers le modèle audio.

        Returns:
            Path: Chemin complet vers le modèle audio
        """
        return ResourceManager.get_resource_path(
            Path("binaries/audio_model/vosk-model-small-fr-0.22")
        )
