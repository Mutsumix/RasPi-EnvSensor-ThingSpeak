import serial
import time
from typing import Optional, Dict
from logging import getLogger, basicConfig, INFO

logger = getLogger(__name__)
basicConfig(level=INFO)
logger.setLevel(INFO)

class OmronSensor:
    """Omronセンサーとの通信を管理するクラス"""

    def __init__(self, port="/dev/ttyUSB1", baudrate=115200):
        """
        OmronSensorクラスの初期化

        Args:
            port (str): シリアルポート名
            baudrate (int): ボーレート
        """
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.last_read_time = 0
        self.read_interval = 1  # 1秒ごとに新しいデータを読み取る

    def connect(self):
        """センサーとのシリアル接続を確立する"""
        if self.ser is None or not self.ser.is_open:
            try:
                self.ser = serial.Serial(self.port, self.baudrate, serial.EIGHTBITS, serial.PARITY_NONE, timeout=1)
                logger.info("Omron sensor connected successfully.")
            except serial.SerialException as e:
                logger.error(f"Failed to connect to Omron sensor: {e}")
                self.ser = None

    def get_data(self) -> Optional[Dict]:
        """
        センサーからデータを取得する

        Returns:
            Optional[Dict]: センサーデータを含む辞書、エラー時はNone
        """
        if self.ser is None or not self.ser.is_open:
            self.connect()
            if self.ser is None:
                return None

        current_time = time.time()
        if current_time - self.last_read_time < self.read_interval:
            time.sleep(self.read_interval - (current_time - self.last_read_time))

        try:
            self.ser.reset_input_buffer()
            command = bytearray([0x52, 0x42, 0x05, 0x00, 0x01, 0x21, 0x50])
            command += self._calc_crc(command, len(command))
            self.ser.write(command)
            time.sleep(0.5)
            data = self.ser.read(56)
            if len(data) != 56:
                logger.error(f"Received incorrect data length: {len(data)} bytes")
                return None
            parsed_data = self._parse_data(data)
            self.last_read_time = time.time()
            return parsed_data
        except serial.SerialException as e:
            logger.error(f"Serial communication error: {e}")
            self.ser = None  # Connection lost, reset the serial object
            return None
        except Exception as e:
            logger.error(f"Data parsing error: {e}")
            return None

    def _calc_crc(self, buf, length) -> bytearray:
        """
        CRC（巡回冗長検査）を計算する

        Args:
            buf (bytearray): CRCを計算するデータ
            length (int): データの長さ

        Returns:
            bytearray: 計算されたCRC
        """
        crc = 0xFFFF
        for i in range(length):
            crc ^= buf[i]
            for _ in range(8):
                carry_flag = crc & 1
                crc >>= 1
                if carry_flag:
                    crc ^= 0xA001
        return bytearray([crc & 0xFF, crc >> 8])

    def _parse_data(self, data) -> Optional[Dict]:
        """
        センサーからの生データを解析する

        Args:
            data (bytes): センサーからの生データ

        Returns:
            Optional[Dict]: 解析されたセンサーデータを含む辞書、エラー時はNone
        """
        if len(data) < 56:
            logger.error("Data length too short to parse.")
            return None
        return {
            'temperature': self._s16(int.from_bytes(data[8:10], byteorder='little', signed=True)) / 100.0,
            'humidity': int.from_bytes(data[10:12], byteorder='little', signed=False) / 100.0,
            'light': int.from_bytes(data[12:14], byteorder='little', signed=False),
            'pressure': int.from_bytes(data[14:18], byteorder='little', signed=False) / 1000.0,
            'noise': int.from_bytes(data[18:20], byteorder='little', signed=False) / 100.0,
            'co2': int.from_bytes(data[22:24], byteorder='little', signed=False)
        }

    def _s16(self, value: int) -> int:
        """16ビット符号付き整数を解釈する"""
        return -(value & 0x8000) | (value & 0x7fff)

    def cleanup(self) -> None:
        """シリアル接続をクリーンアップする"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            logger.info("Serial port closed.")
        self.ser = None
