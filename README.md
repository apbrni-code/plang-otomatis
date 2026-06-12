# Unhan RI Data Pipeline & OCR System

Proyek ini adalah sistem backend dan *data pipeline* untuk memproses tangkapan gambar dari kamera OCR di gerbang kampus Universitas Pertahanan (Unhan) RI. Sistem ini dibangun dengan fokus pada arsitektur yang *scalable*, *real-time logging*, dan efisiensi *query* database.

## 🚀 Fitur Utama
- **Real-time Ingestion**: API menerima hasil bacaan OCR secara *asynchronous* tanpa *bottleneck*.
- **Relational Database**: Skema data yang dinormalisasi untuk menyimpan Personel, Kendaraan, dan Log Akses.
- **Database Migration**: Terintegrasi dengan Alembic untuk melacak perubahan skema database secara otomatis.
- **Analytics Ready**: Endpoint khusus yang bisa diintegrasikan dengan aplikasi Dashboard / *Business Intelligence* (BI).

## 🛠 Teknologi yang Digunakan
- **Python 3**
- **FastAPI** (Web Framework)
- **SQLAlchemy** (ORM)
- **Supabase / PostgreSQL** (Database Production)
- **Alembic** (Database Migration)
- **EasyOCR** (Untuk simulasi/seeding data)

## 📦 Cara Menjalankan Proyek

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Environment Variables**
   Buat file `.env` di direktori utama, dan tambahkan string koneksi Supabase Anda:
   ```env
   DATABASE_URL="postgresql://user:password@host:port/database"
   ```

3. **Jalankan Database Migrations (Opsional)**
   Pastikan skema database *up-to-date*:
   ```bash
   alembic upgrade head
   ```

4. **Jalankan API Server**
   ```bash
   uvicorn api.main:app --reload
   ```

5. **Akses Dokumentasi API**
   Buka browser dan kunjungi: `http://127.0.0.1:8000/docs`

## 📊 Analytics Dashboard
Anda dapat mengakses endpoint `GET /api/v1/analytics/daily-traffic` untuk mendapatkan rekap data masuk dan keluar kendaraan secara real-time.
