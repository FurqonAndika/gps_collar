import requests
import os 
import configparser

def send_message(message_text):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(BASE_DIR, 'mqtt_config.ini')
    # Baca konfigurasi dari config.ini
    config = configparser.ConfigParser()
    config.read(config_path)
        
    TELEGRAM_TOKEN = config['TELEGRAM']['telegram_token']
    CHAT_ID = config['TELEGRAM']['chat_id']

    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {
        'chat_id': CHAT_ID,
        'text': message_text
    }

    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"❌ Gagal kirim Telegram: {response.status_code}, {response.text}")
    except Exception as e:
        print("❌ Exception saat kirim Telegram:", e)
