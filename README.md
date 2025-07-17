# 🛰️ GPS Collar Satwa – Django + Docker + JWT

Aplikasi ini digunakan untuk memantau data satwa seperti lokasi GPS, suhu, dan baterai secara real-time. Dibangun menggunakan **Django**, **DRF**, **JWT**, dan dideploy menggunakan **Docker**.

---

## 📁 Struktur Folder

```
GPS_COLLAR_PROJECT/
│
├── account_app/             # App autentikasi dan user
├── api_app/                 # App data sensor dan tracking
├── gps_collar_project/      # Pengaturan utama Django (settings, wsgi, asgi)
├── media/                   # Upload media files (image, dll)
├── static/                  # Static files (CSS, JS)
│
├── db.sqlite3               # Default SQLite (bisa diabaikan jika pakai PostgreSQL)
├── manage.py                # Django CLI
│
├── Dockerfile               # Docker build instructions
├── docker-compose.yml       # Layanan: web & database
├── entrypoint.sh            # Shell script saat container start
├── requirements.txt         # Daftar dependency pip
└── README.md                # (← file ini)
```

---

## 🚀 Menjalankan dengan Docker

### 1. Build dan Jalankan

```bash
docker-compose up --build
```

> Jika ingin menjalankan ulang tanpa rebuild:
```bash
docker-compose up
```

### 2. Mengakses Aplikasi

| Akses                    | URL                        |
|--------------------------|-----------------------------|
| API Root                 | http://localhost:8010/      |
| Django Admin             | http://localhost:8010/admin |
| PostgreSQL Host          | `db`, port `5433` (dalam container) |

---

## 🛠️ Perintah Docker Penting

| Tujuan                          | Perintah                                                  |
|----------------------------------|------------------------------------------------------------|
| Melihat container aktif         | `docker ps`                                               |
| Masuk ke dalam container web    | `docker exec -it gps_collar_web bash`                    |
| Membuat superuser Django        | `python manage.py createsuperuser` (dalam container web) |
| Melihat log container           | `docker logs gps_collar_web`                             |

---

## 🔐 Autentikasi & Role

Menggunakan JWT Token:

- **Superadmin**: Bisa buat dan hapus semua user
- **Admin**: Hanya bisa membuat & menghapus user dari instansi yang sama
- **Guest**: Hanya bisa melihat data

Header untuk permintaan API:

```
Authorization: Bearer <access_token>
```

---

## 🧪 Testing Login

```json
POST /api/login/

{
  "username": "admin",
  "password": "admin123"
}
```

Response:

```json
{
  "message": "Login Successful",
  "tokens": {
    "access": "<jwt-access-token>",
    "refresh": "<jwt-refresh-token>"
  },
  "role": 2,
  "is_staff": true
}
```

---

## ⚙️ Database

Gunakan PostgreSQL dengan konfigurasi ENV:

```
DB_NAME=gps_collar
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5433
```

---

## 📦 Dependency (requirements.txt)

Termasuk:
- Django
- djangorestframework
- psycopg2-binary
- Pillow
- JWT (simplejwt)
- dll.

---

## 📍 Catatan

- Untuk tracking satwa, gunakan `api_app.models.SensorDataModel`
- Geofence dan area bisa ditambahkan melalui `AreaModel`
- Visualisasi bisa dibangun di frontend (Vue/React) menggunakan websocket atau API polling.

---

## 🧹 Maintenance

- Bersihkan container lama:
```bash
docker system prune -af
```

- Bersihkan image lama:
```bash
docker rmi <image_id>
```

---

## 👨‍💻 Author

> Furqon Andika – 2025  
> Politeknik Caltex Riau
