import qrcode
from pathlib import Path
from PyQt6.QtCore import QObject


from src.core.event_handler import events
from src.core.logging_config import logger
from src.core.streaming.streaming_service import StreamingService
from src.utils.resource_manager import ResourceManager


class GoProService(QObject):
    """
    Service managing GoPro camera connection and control.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_connected = True
        self.streaming_service = StreamingService(self)

    def connect(self):
        """
        Establish connection with GoPro.
        """
        try:
            # TODO: Implement GoPro connection
            self.is_connected = True
            events.connected.emit()
        except Exception as e:
            events.connection_error.emit(str(e))

    def start_streaming(self) -> bool:
        """
        Start RTMP streaming from GoPro.
        """
        try:
            if not self.streaming_service.start_mediamtx():
                logger.error("Error starting MediaMTX server")
                return False

            rtmp_url = ResourceManager.get_gopro_rtmp_url()
            logger.info(f"Streaming started at {rtmp_url}")
            return True
        except Exception as e:
            events.streaming_error.emit(f"Error starting stream: {str(e)}")
            return False

    def stop_streaming(self) -> bool:
        """
        Stop RTMP streaming.
        """
        try:
            return self.streaming_service.stop_mediamtx()
        except Exception as e:
            events.streaming_error.emit(f"Error stopping stream: {str(e)}")
            return False

    def qrcode_gopro(self, content: str):
        qrcode_dir = ResourceManager.get_app_data_paths("qrcode")
        qrcode_dir.mkdir(parents=True, exist_ok=True)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)

        filename = qrcode_dir / "gopro_qrcode.png"
        image = qr.make_image(fill_color="black", back_color="white")
        image.save(str(filename))

        events.qrcode_created.emit(f"QR code generated: {filename}")

    def generate_wifi_qrcode(self, ssid: str, password: str):
        """
        Generate WiFi QR code with special format
        !MJOIN="SSID:PASSWORD" used by GoPro cameras.
        """
        qrcode_dir = ResourceManager.get_app_data_paths("qrcode")
        qrcode_dir.mkdir(parents=True, exist_ok=True)

        content = f'!MJOIN="{ssid}:{password}"'

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)

        filename = qrcode_dir / "wifi_qrcode.png"
        image = qr.make_image(fill_color="black", back_color="white")
        image.save(str(filename))

        events.qrcode_created.emit(f"WiFi QR code generated: {filename}")
        return str(filename)

    def disconnect(self):
        """
        Disconnect from GoPro.
        """
        try:
            self.stop_streaming()

            # TODO: Implement GoPro disconnection
            self.is_connected = False
            events.disconnected.emit()
        except Exception as e:
            events.connection_error.emit(str(e))
