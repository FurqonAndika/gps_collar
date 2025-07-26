from django.core.management.base import BaseCommand
import configparser
import os
import time
import random
import paho.mqtt.client as mqtt

class Command(BaseCommand):
    help = 'Simulasi pengiriman data gajah via MQTT setiap 10 detik'

    def handle(self, *args, **kwargs):
        self.stdout.write("📡 Memulai simulator pengiriman data...")

        # Baca konfigurasi dari mqtt_config.ini
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(BASE_DIR, 'mqtt_config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)

        mqtt_host = config['MQTT']['host']
        mqtt_port = int(config['MQTT']['port'])
        mqtt_user = config['MQTT']['username']
        mqtt_pass = config['MQTT']['password']
        mqtt_topic = config['MQTT']['topic'].strip('"')

        # Inisialisasi MQTT client
        client = mqtt.Client()
        if mqtt_user and mqtt_pass:
            client.username_pw_set(mqtt_user, mqtt_pass)

        # Connect ke broker
        self.stdout.write(f"🔌 Connecting to MQTT broker at {mqtt_host}:{mqtt_port}")
        client.connect(mqtt_host, mqtt_port)
        client.loop_start()

        try:
            while True:
                node_serial = "1234567890"
                gateway_serial = "1234567890"

                # sekitaran pekanbaru                  
                lon = round(random.uniform(101.40, 101.47), 8)
                lat = round(random.uniform(0.55, 0.63), 8)
                rssi = round(random.uniform(25, 40), 1)


                message = f"{node_serial},{lon},{lat},{rssi},{gateway_serial}"
                self.stdout.write(f"📤 Publishing: {message}")
                client.publish(mqtt_topic, message)


                node_serial = "0987654321"

                # sekitaran pekanbaru                  
                lat = round(random.uniform(0.55, 0.63), 8)
                lon = round(random.uniform(101.40, 101.47), 8)
                rssi = round(random.uniform(25, 40), 1)
                

                message = f"{node_serial},{lon},{lat},{rssi},{gateway_serial}"
                self.stdout.write(f"📤 Publishing: {message}")
                client.publish(mqtt_topic, message)

                time.sleep(6)

        except KeyboardInterrupt:
            self.stdout.write("❌ Simulator dihentikan.")
            client.loop_stop()
            client.disconnect()
