# Data Engineer Scope of Work

Dokumen ini merangkum cakupan kerja (scope) dari peran Data Engineer dalam pengembangan sistem Data Pipeline Unhan RI.

## 1. Merancang Skema Database
Membangun struktur relasional yang efisien (Normalized) namun tetap cepat untuk query (OLTP). Tabel utama yang dikelola:
- **User**: Autentikasi dan otorisasi akses dasbor.
- **Personel**: Data master pemilik kendaraan (TNI AD, AL, AU, Polri, Sipil, dll).
- **Kendaraan**: Entitas kendaraan beserta atribut tipe platnya.
- **Jenis Plat**: Referensi tipe plat nomor (berdasarkan matra/institusi).
- **Gerbang**: Referensi lokasi kamera/gerbang.
- **Log Akses**: Tabel transaksi bervolume tinggi yang mencatat waktu dan status gerak (Masuk/Keluar).

## 2. Mendesain Data Pipeline OCR
Membangun jalur pipa data yang menghubungkan perangkat edge (Kamera/Mesin OCR) menuju server pusat:
- Memastikan API sanggup menerima *ingestion* data bervolume tinggi tanpa putus.
- Menangani *data cleansing* (pembersihan karakter yang salah baca oleh OCR).
- Menangani data tidak terdaftar (Tamu/Salah Baca).

## 3. Mendesain Strategi Realtime Logging
- Menerapkan *Background Tasks* atau antrean (Message Broker/Queue) agar permintaan dari kamera dapat langsung direspons seketika (Latensi < 100ms).
- Memastikan tidak ada *race condition* saat menulis log ke database.

## 4. Mendesain Scalable Architecture
- Mempersiapkan migrasi dari RDBMS lokal (SQLite) ke layanan *Cloud Database* terskala seperti Supabase/PostgreSQL.
- Menyiapkan alat *Database Migration* (misalnya Alembic) untuk memastikan skema database dapat diperbarui dan dikontrol versinya seiring berjalannya proyek.

## 5. Menyiapkan Fondasi Analytics untuk Masa Depan
- Menyusun arsitektur untuk kebutuhan *Business Intelligence* (BI) di masa mendatang.
- Memikirkan strategi ekstraksi data operasional (OLTP) ke bentuk *Data Warehouse* (OLAP) untuk keperluan *Dashboard* analitik dan *Reporting* bulanan tanpa membebani server utama.
