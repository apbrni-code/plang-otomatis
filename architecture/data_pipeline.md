# Arsitektur Data Pipeline — Sistem Plang Otomatis Unhan RI

Dokumen ini menjelaskan alur data secara end-to-end dari perangkat kamera OCR di gerbang kampus hingga lapisan analytics/dashboard.

---

## 1. Gambaran Umum Alur Data

```
[Kamera OCR / IoT Edge]
        │
        │  HTTP POST /api/v1/ocr-ingest
        ▼
[FastAPI Server]
        │
        ├──► [Background Task Worker]
        │           │
        │           ▼
        │    [Data Cleansing & Validation]
        │           │  - Normalisasi plat nomor
        │           │  - Handle salah baca (karakter ambigu)
        │           │  - Klasifikasi: Terdaftar / Tamu
        │           │
        │           ▼
        │    [PostgreSQL / Supabase — OLTP]
        │           │
        │           ├── Tabel: Personel
        │           ├── Tabel: Kendaraan
        │           ├── Tabel: LogAkses  ◄── Volume tinggi
        │           └── Tabel: Admin
        │
        └──► [Response 202 Accepted] → Kamera lanjut
                                        (latensi < 100ms)
```

---

## 2. Tahapan Pipeline Detail

### Stage 1 — Ingestion (Edge → API)
- **Aktor**: Perangkat IoT (kamera + modul OCR)
- **Protokol**: HTTP POST ke endpoint `/api/v1/ocr-ingest`
- **Payload**: `{ platNomor, jenisAkses, statusBuka, instansi }`
- **Jaminan**: API langsung merespons `202 Accepted` tanpa menunggu DB selesai
- **Mekanisme**: FastAPI `BackgroundTasks` — proses insert DB berjalan di background

### Stage 2 — Cleansing & Validation
- Normalisasi karakter OCR yang ambigu: `0↔O`, `1↔I`, `8↔B`
- Cek keberadaan `platNomor` di tabel `Kendaraan`
- Jika tidak ditemukan → buat entri `Kendaraan` sementara dengan `instansi = "Tamu"`
- Jika ditemukan → langsung tulis ke `LogAkses`

### Stage 3 — Persistence (OLTP)
- Database utama: **PostgreSQL via Supabase**
- ORM: **SQLAlchemy**
- Migration: **Alembic** (setiap perubahan skema ter-versioning)
- Tabel `LogAkses` adalah tabel transaksi bervolume tinggi — diindeks pada kolom `platNomor` dan `waktuAkses`

### Stage 4 — Analytics Layer (Downstream)
- Data dari `LogAkses` dapat diekstrak untuk kebutuhan BI/dashboard
- Lihat `scalability.md` untuk strategi pemisahan OLTP dan OLAP

---

## 3. Diagram Komponen Sistem Lengkap

```
┌─────────────────────────────────────────────────────────┐
│                      GERBANG KAMPUS                      │
│                                                          │
│   [Kamera]──►[Modul OCR]──►[IoT Controller]             │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP (LAN/WiFi)
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    SERVER BACKEND                        │
│                                                          │
│   [FastAPI]──►[BackgroundTask]──►[SQLAlchemy ORM]       │
│       │                                  │               │
│       ▼                                  ▼               │
│   [Response]               [PostgreSQL / Supabase]       │
│   202 Accepted                           │               │
└──────────────────────────────────────────┼──────────────┘
                                           │
                          ┌────────────────┼──────────────┐
                          │         ANALYTICS LAYER        │
                          │                │               │
                          │   [Read Replica / View]        │
                          │                │               │
                          │   [Dashboard / BI Tool]        │
                          └───────────────────────────────┘
```

---

## 4. Keputusan Desain & Rasionalisasi

| Keputusan | Alasan |
|---|---|
| `BackgroundTasks` untuk insert DB | Memastikan latensi respons ke kamera < 100ms |
| Supabase/PostgreSQL sebagai DB | Skalabilitas cloud, sudah production-ready |
| Alembic untuk migrasi | Perubahan skema ter-versioning, aman untuk tim |
| Indeks pada `platNomor` & `waktuAkses` | Query log cepat meskipun volume jutaan baris |
| Tamu otomatis dibuat sebagai kendaraan dummy | Tidak ada log yang terbuang, semua terekam |

---

## 5. Keterbatasan & Rencana Pengembangan

- **Saat ini**: Pipeline bersifat *synchronous-per-request*, belum menggunakan message broker
- **Ke depan**: Jika volume kamera bertambah (>10 gerbang), pertimbangkan **Redis Queue / Celery** sebagai message broker untuk menggantikan `BackgroundTasks`
- **Fault tolerance**: Belum ada retry mechanism jika insert DB gagal — perlu ditambahkan dead-letter queue
