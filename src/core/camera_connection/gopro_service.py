import qrcode
import os
from PyQt6.QtCore import QObject

from src.core.event_handler import events
from src.core.constants import qrcode_path
from src.core.streaming.streaming_service import StreamingService


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
                print("Error starting MediaMTX server")
                return False

            rtmp_url = self.streaming_service.get_stream_url()
            print(f"Streaming started at {rtmp_url}")
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
        if not os.path.exists(qrcode_path):
            os.makedirs(qrcode_path)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)

        filename = os.path.join(qrcode_path, "gopro_qrcode.png")
        image = qr.make_image(fill_color="black", back_color="white")
        image.save(filename)

        events.qrcode_created.emit(f"QR code generated: {filename}")

    def generate_wifi_qrcode(self, ssid: str, password: str):
        """
        Generate WiFi QR code with special format
        !MJOIN="SSID:PASSWORD" used by GoPro cameras.
        """
        if not os.path.exists(qrcode_path):
            os.makedirs(qrcode_path)

        content = f'!MJOIN="{ssid}:{password}"'

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)

        filename = os.path.join(qrcode_path, "wifi_qrcode.png")
        image = qr.make_image(fill_color="black", back_color="white")
        image.save(filename)

        events.qrcode_created.emit(f"WiFi QR code generated: {filename}")
        return filename

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
