import os
import socket
from pathlib import Path

from src.core.logging_config import logger


# Paths configuration
src_path = os.path.dirname(os.path.dirname(__file__))
fonts_path = os.path.join(src_path, "ui", "assets", "fonts")
styles_path = os.path.join(src_path, "ui", "styles", "styles.qss")
qrcode_path = os.path.join(src_path, "storage", "qrcode")
logo_path = os.path.join(src_path, "ui", "assets", "images", "Logo-CookiNUM-v.svg")
icons_path = os.path.join(src_path, "ui", "assets", "icons")
assets_path = os.path.join(src_path, "ui", "assets")
video_files_path = os.path.join(src_path, "storage", "video_files")
tags_path = os.path.join(src_path, "storage", "tags")
workspace_root = os.path.dirname((os.path.dirname(os.path.dirname(__file__))))
mediamtx_path = os.path.join(workspace_root, "ressources", "mediamtx", "mediamtx.exe")
mediamtx_config = os.path.join(workspace_root, "ressources", "mediamtx", "mediamtx.yml")

# Streaming configuration
streaming_rtmp_url = "rtmp://localhost:1935/live/stream"
streaming_rtsp_url = "rtsp://localhost:8554/live/stream"

# Audio model paths
audio_model_path_fr = os.path.join(
    workspace_root, "ressources", "audio_model", "vosk-model-small-fr-0.22"
)
audio_model_path_us = os.path.join(
    workspace_root, "ressources", "audio_model", "vosk-model-small-en-us-0.15"
)


def get_ipv4_address():
    """Get the local IPv4 address."""
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address


# GoPro streaming URL
streaming_rtmp_url_gopro = f"rtmp://{get_ipv4_address()}:1935/live/stream"

# Log IP address at startup
logger.info(f"IP address: {get_ipv4_address()}")
