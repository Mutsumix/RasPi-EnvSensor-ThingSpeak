import yaml
import time
import schedule
import requests
from omron_sensor import OmronSensor
from logging import getLogger, basicConfig, INFO

# ログの設定
logger = getLogger(__name__)
basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    """設定ファイル（config.yml）を読み込む"""
    with open('config.yml', 'r') as file:
        return yaml.safe_load(file)

def send_data_to_thingspeak(api_key, data):
    """センサーデータをThingSpeakに送信する

    Args:
        api_key (str): ThingSpeakのAPIキー
        data (dict): センサーから取得したデータ
    """
    url = f"https://api.thingspeak.com/update?api_key={api_key}"
    payload = {
        "field1": data['temperature'],
        "field2": data['humidity'],
        "field3": data['light'],
        "field4": data['pressure'],
        "field5": data['noise'],
        "field6": data['co2']
    }
    response = requests.get(url, params=payload)
    if response.status_code == 200:
        logger.info("Data sent to ThingSpeak successfully")
    else:
        logger.error(f"Failed to send data to ThingSpeak. Status code: {response.status_code}")

def monitor_and_send():
    """センサーデータを取得し、ThingSpeakに送信する"""
    config = load_config()
    sensor = OmronSensor(port=config['sensor']['omron']['port'])
    sensor.connect()  # 明示的に接続を確立

    try:
        data = sensor.get_data()
        if data:
            send_data_to_thingspeak(
                config['thingspeak']['api_key'],
                data
            )
        else:
            logger.error("Failed to get sensor data")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        sensor.cleanup()

def main():
    """メイン関数: スケジューラーを設定し、定期的にデータを送信する"""
    config = load_config()
    # 設定ファイルで指定された間隔でmonitor_and_send関数を実行するようスケジュール
    schedule.every(config['sensor']['scheduler']['interval_minutes']).minutes.do(monitor_and_send)

    logger.info("Monitoring started. Press Ctrl+C to exit.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user.")

if __name__ == "__main__":
    main()
