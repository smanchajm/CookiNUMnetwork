import os


root_path = os.path.dirname(os.path.dirname(__file__))
fonts_path = os.path.join(root_path, "ui", "assets", "fonts")
qrcode_path = os.path.join(root_path, "storage", "qrcode")
logo_path = os.path.join(root_path, "ui", "assets", "images", "Logo-CookiNUM-v.svg")
icons_path = os.path.join(root_path, "ui", "assets", "icons")
assets_path = os.path.join(root_path, "ui", "assets")
video_files_path = os.path.join(root_path, "storage", "video_files")
workspace_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
)
mediamtx_path = os.path.join(root_path, "ressources", "mediamtx", "mediamtx.exe")
mediamtx_config = os.path.join(root_path, "ressources", "mediamtx", "mediamtx.yml")
