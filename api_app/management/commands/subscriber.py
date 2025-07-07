from django.core.management.base import BaseCommand
import configparser,os
import paho.mqtt.client as mqtt
from api_app.models import RawSensorDataModel,SensorDataModel, Zoo, AreaModel
from django.utils.timezone import now
import uuid
from .geofence import is_inside_geofence

class Command(BaseCommand):
    help = 'Subscriber mqtt'

    def handle(self, *args, **kwargs):
        self.stdout.write("start subcribe")

        # Cari path config.ini yang berada di folder yang sama dengan script ini
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(BASE_DIR, 'mqtt_config.ini')
        # Baca konfigurasi dari config.ini
        config = configparser.ConfigParser()
        config.read(config_path)

        mqtt_host = config['MQTT']['host']
        mqtt_port = int(config['MQTT']['port'])
        mqtt_user = config['MQTT']['username']
        mqtt_pass = config['MQTT']['password']
        mqtt_topic = config['MQTT']['topic'].strip('"')

       # Callback ketika pesan masuk
        def on_message(client, userdata, msg):
            message = msg.payload.decode()
            topik = msg.topic
            waktu = now()

            print(f"[{topik}] {message}")

            # 1. Simpan ke RawSensorDataModel
            '''
            try:
                RawSensorDataModel.objects.get_or_create(
                    message=message,
                    time=waktu,
                    defaults={
                        'created_at': waktu,
                        'topik': topik,
                    }
                )
            except Exception as e:
                print("Gagal simpan ke RawSensorDataModel:", e)
            '''
            # 2. Parsing pesan
            try:
                parts = message.strip().split(',')
                if len(parts) != 5:
                    print(" Format tidak sesuai (harus 5 elemen):", message)
                    return

                satelit_id, lon, lat, temperature, battery = parts

                # Konversi nilai ke tipe data yang sesuai
                lon = float(lon)
                lat = float(lat)
                temperature = float(temperature)
                battery = float(battery)

                # Cari Zoo berdasarkan satelit_serial
                try:
                    zoo = Zoo.objects.get(satelit_serial=satelit_id)
                except Zoo.DoesNotExist:
                    print(f" Zoo dengan satelit_serial '{satelit_id}' tidak ditemukan.")
                    zoo = None  # Tetap simpan meski tanpa relasi

                # Simpan ke SensorDataModel
                '''
                SensorDataModel.objects.create(
                    zoo=zoo,
                    time=waktu,
                    created_at=waktu,
                    latitude=lat,
                    longitude=lon,
                    temperature=temperature,
                    battery=battery
                )'''
                print("✔️ Data Sensor berhasil disimpan.")

                for area in AreaModel.objects.all():
                    in_geofence, distance = is_inside_geofence(
                        lat, lon,
                        float(area.latitude), float(area.longitude),
                        area.radius_km
                    )

                    if in_geofence:
                        print(f"📍 Gajah {zoo.name} masuk ke area '{area.place_name}' (Jarak: {distance:.2f} km)")
                        # 👉 Tambahkan aksi di sini: misalnya simpan log, kirim notifikasi, dll.
                    else:
                        print(f"📍 Gajah {zoo.name} di luar area '{area.place_name}' (Jarak: {distance:.2f} km)")
                        
            except Exception as e:
                print("Gagal parsing/simpan SensorDataModel:", e)



        # Inisialisasi MQTT client
        client = mqtt.Client()
        # Hanya set username/password kalau tidak kosong
        if mqtt_user and mqtt_pass:
            client. username_pw_set(mqtt_user, mqtt_pass)

        client.on_message = on_message

        # Koneksi ke broker
        print(f"Connecting to {mqtt_host}:{mqtt_port}...")
        client.connect(mqtt_host, mqtt_port)

        # Subscribe ke topik
        client.subscribe(mqtt_topic)
        print(f"Subscribed to topic: {mqtt_topic}")

        # Loop forever
        client.loop_forever()
