from django.core.management.base import BaseCommand
import configparser,os
import paho.mqtt.client as mqtt
from api_app.models import RawSensorDataModel,SensorDataModel, Zoo, AreaModel, GatewayModel
from django.utils.timezone import now
import uuid
from .geofence import is_inside_geofence, calculate_distance
from .gps_bot_telegram import send_message
import time

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
            topic = msg.topic
            waktu = now()

            # 1. Simpan ke RawSensorDataModel
            
            try:
                RawSensorDataModel.objects.get_or_create(
                    message=message,
                    time=waktu,
                    defaults={
                        'created_at': waktu,
                        'topic': topic,
                    }
                )
            except Exception as e:
                print("Gagal simpan ke RawSensorDataModel:", e)
            
            # 2. Parsing pesan
            try:
                parts = message.strip().split(',')
                if len(parts) != 5:
                    print(" Format tidak sesuai (harus 5 elemen):", message)
                    return

                node_serial, lon, lat, rssi, gateway_serial = parts

                # Konversi nilai ke tipe data yang sesuai
                lon = float(lon)
                lat = float(lat)
                rssi = float(rssi)
                gateway_serial = int(gateway_serial)
                distance_from_gateway=None

                # Cari Zoo berdasarkan node_serial
                try:
                    zoo = Zoo.objects.get(node_serial=node_serial)
                except Zoo.DoesNotExist:
                    print(f" Zoo dengan node_serial '{node_serial}' tidak ditemukan.")
                    zoo = None  # Tetap simpan meski tanpa relasi

                try:
                    gateway = GatewayModel.objects.get(gateway_serial=gateway_serial)
                    distance_from_gateway = calculate_distance(lat,lon, float(gateway.latitude),float(gateway.longitude))
                    print("distance_from_gateway :", distance_from_gateway)
                except Exception as e:
                    print(e)
                    gateway = None  # Tetap simpan meski tanpa relasi
                
                # Simpan ke SensorDataModel
                data = SensorDataModel.objects.create(
                    zoo=zoo,
                    time=waktu,
                    created_at=waktu,
                    latitude=lat,
                    longitude=lon,
                    rssi=rssi,
                    gateway=gateway,
                    distance_from_gateway= distance_from_gateway
                )
                # print("✔️ Data Sensor berhasil disimpan.")
                
                detected_areas = []

                for area in AreaModel.objects.all():
                    in_geofence, distance = is_inside_geofence(
                        lat, lon,
                        float(area.latitude), float(area.longitude),
                        area.radius_km
                    )

                    if in_geofence:
                        detected_areas.append({
                            "name": area.place_name,
                            "distance": distance
                        })

                # Hanya kirim pesan jika terdeteksi masuk minimal 1 area
                if detected_areas:
                    area_list = "\n".join([
                        f"• {a['name']} (📏 {a['distance']:.2f} km)"
                        for a in detected_areas
                    ])

                    telegram_message = (
                        f"🦣 Gajah {zoo.name} terdeteksi MASUK ke area berikut:\n"
                        f"{area_list}\n\n"
                        f"📍 Lokasi: [{lon:.6f}, {lat:.6f}](https://www.google.com/maps?q={lon:.6f},{lat:.6f})\n"
                        # f"🌡️ sinyal: {rssi}db, 🔋 jarak dari Gateway: {distance}%"
                    )
                    # print(telegram_message)
                    start = time.time()
                    send_message(telegram_message)
                    print(time.time()-start)
                else:
                    print(f"📍 Gajah {zoo.name} tidak berada di dalam geofence mana pun.")
        
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

        # Subscribe ke topic
        client.subscribe(mqtt_topic)
        print(f"Subscribed to topic: {mqtt_topic}")

        # Loop forever
        client.loop_forever()
