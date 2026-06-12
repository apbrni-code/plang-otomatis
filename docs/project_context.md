# Project Context: Unhan RI Data Pipeline & OCR System

## Latar Belakang
Proyek ini merupakan sistem pemantauan dan pencatatan akses gerbang kampus Universitas Pertahanan (Unhan) RI. Sistem ini memanfaatkan teknologi *Optical Character Recognition* (OCR) untuk membaca plat nomor kendaraan yang masuk atau keluar, kemudian secara otomatis merekam log akses tersebut ke dalam database.

## Tujuan Utama
Membangun *data pipeline* yang tangguh, cepat, dan terukur untuk memproses hasil tangkapan gambar kamera OCR secara real-time. Sistem dirancang untuk mampu menangani beban akses yang tinggi tanpa mengalami bottleneck pada level API maupun database.

## Arsitektur Sistem (Current State)
1. **Edge Node (Kamera / OCR)**:
   Perangkat kamera di gerbang akan menangkap gambar, menjalankan model OCR (misalnya EasyOCR), dan mengirimkan *payload* (plat nomor dan status gerak) ke API pusat.
2. **Backend API (FastAPI)**:
   Menerima HTTP POST request dari kamera. Menggunakan fitur `BackgroundTasks` untuk memastikan *response* API yang instan (202 Accepted) sementara proses validasi dan *insert* database berjalan secara asinkron di belakang layar.
3. **Database (SQLite -> Supabase/PostgreSQL)**:
   Saat ini menggunakan SQLite untuk environment *development* dengan bantuan ORM SQLAlchemy. Direncanakan untuk migrasi ke PostgreSQL (Supabase) untuk environment produksi.

## Struktur Database Inti
- `users`: Data admin/pengguna sistem.
- `personel`: Data anggota militer/sipil Unhan (Nama, NIP, Pangkat, Jabatan).
- `kendaraan`: Data kendaraan yang terdaftar (terhubung ke personel dan memiliki tipe plat militer/sipil).
- `log_akses`: Catatan riwayat keluar-masuk kendaraan secara real-time.
