import os
import socket

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
streaming_rtmp_url = "rtmp://localhost:1935/live/stream"
streaming_rtsp_url = "rtsp://localhost:8554/live/stream"
audio_model_path_fr = os.path.join(
    workspace_root, "ressources", "audio_model", "vosk-model-small-fr-0.22"
)
audio_model_path_us = os.path.join(
    workspace_root, "ressources", "audio_model", "vosk-model-small-en-us-0.15"
)


def get_ipv4_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address


streaming_rtmp_url_gopro = f"rtmp://{get_ipv4_address()}:1935/live/stream"

print("Test: get_ipv4_address", get_ipv4_address())
