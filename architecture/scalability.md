# Strategi Skalabilitas & Arsitektur OLTP → OLAP

Dokumen ini menjelaskan strategi untuk memastikan sistem tetap performan saat data berkembang, serta rancangan transisi dari database operasional (OLTP) menuju infrastruktur analitik (OLAP).

---

## 1. Pemisahan OLTP dan OLAP

### Apa Perbedaannya?

| Aspek | OLTP (Operasional) | OLAP (Analitik) |
|---|---|---|
| **Tujuan** | Insert/update real-time dari kamera | Query besar untuk dashboard/reporting |
| **Pola Query** | Row-by-row, cepat, per transaksi | Agregasi besar (SUM, COUNT, GROUP BY) |
| **Beban** | Tinggi & konstan (24 jam) | Sporadis, besar |
| **Database** | PostgreSQL / Supabase (OLTP) | Data Warehouse / Materialized View |
| **Dampak jika dicampur** | Query analitik berat → server OLTP lambat → kamera delay |  |

### Prinsip Utama
> **Query analitik TIDAK boleh dijalankan langsung ke database operasional saat jam sibuk.**

---

## 2. Strategi Jangka Pendek (Sekarang)

Untuk fase awal capstone ini, strategi yang digunakan adalah **Materialized View** dan **Read Replica logis** menggunakan fitur bawaan PostgreSQL/Supabase.

### 2a. Endpoint Analytics via Aggregated Query
- Endpoint `/api/v1/analytics/*` di FastAPI menjalankan query agregasi ke DB
- Diperbolehkan selama data masih < 1 juta baris dan tidak diakses real-time oleh kamera
- Query dioptimasi dengan indeks pada `waktuAkses` dan `instansi`

### 2b. Indeks yang Direkomendasikan
```sql
-- Untuk query per waktu (peak hours, daily traffic)
CREATE INDEX idx_log_waktu ON "LogAkses" ("waktuAkses");

-- Untuk query per instansi
CREATE INDEX idx_log_instansi ON "LogAkses" ("instansi");

-- Untuk query per status
CREATE INDEX idx_log_status ON "LogAkses" ("statusBuka");
```

---

## 3. Strategi Jangka Panjang (Roadmap)

### 3a. Read Replica (Supabase)
Supabase mendukung **Read Replica** secara native. Semua query analitik diarahkan ke replica, bukan ke database utama.

```
[Kamera OCR] ──► [DB Utama / Primary]  ← Hanya untuk INSERT/UPDATE
                          │
                     Replikasi otomatis
                          │
                          ▼
[Dashboard / BI] ──► [Read Replica]  ← Hanya untuk SELECT / Analytics
```

### 3b. Data Warehouse — Skema Bintang (Star Schema)

Untuk kebutuhan reporting bulanan dan BI di masa depan, data dari OLTP diekstrak dan ditransformasi ke skema Data Warehouse:

```
                    ┌─────────────────┐
                    │  fact_log_akses │  ← Tabel Fakta
                    │─────────────────│
                    │ id_log (PK)     │
                    │ id_waktu (FK)   │──────► dim_waktu
                    │ id_kendaraan(FK)│──────► dim_kendaraan
                    │ id_instansi (FK)│──────► dim_instansi
                    │ status_buka     │
                    │ jenis_akses     │
                    └─────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   dim_waktu      │     │  dim_kendaraan   │     │  dim_instansi    │
│──────────────────│     │──────────────────│     │──────────────────│
│ id_waktu (PK)    │     │ id_kendaraan(PK) │     │ id_instansi (PK) │
│ tanggal          │     │ plat_nomor       │     │ nama_instansi    │
│ jam              │     │ jenis_kendaraan  │     │ kategori         │
│ hari_dalam_minggu│     │ nip_personel     │     │ (TNI/Polri/Sipil)│
│ bulan            │     │ nama_personel    │     └──────────────────┘
│ tahun            │     │ pangkat          │
│ adalah_hari_libur│     └──────────────────┘
└──────────────────┘
```

### 3c. Proses ETL (Extract, Transform, Load)

```
[PostgreSQL OLTP]
      │
      │  Jadwal: setiap malam pukul 00.00
      │  Tool: Python script / Airflow DAG
      ▼
[Transformasi & Cleansing]
      │  - Denormalisasi untuk OLAP
      │  - Isi dimensi yang kosong
      │  - Handle NULL / outlier
      ▼
[Data Warehouse / PostgreSQL OLAP]
      │
      ▼
[Dashboard / BI Tool]
(Metabase / Grafana / Superset)
```

---

## 4. Kapan Harus Upgrade Infrastruktur?

| Kondisi | Tindakan yang Direkomendasikan |
|---|---|
| Data `LogAkses` < 500.000 baris | Query langsung ke OLTP masih aman |
| Data `LogAkses` 500k – 5 juta baris | Aktifkan Read Replica di Supabase |
| Data > 5 juta baris | Implementasikan ETL ke Data Warehouse terpisah |
| > 10 gerbang aktif bersamaan | Tambahkan Redis Queue / Celery sebagai buffer ingestion |

---

## 5. Kesimpulan

Untuk **fase capstone saat ini**, arsitektur sudah cukup skalabel dengan:
- ✅ Indeks pada kolom kritis di `LogAkses`
- ✅ Background Task untuk ingestion tanpa blocking
- ✅ Supabase/PostgreSQL yang sudah cloud-native

Langkah berikutnya yang perlu disiapkan oleh tim backend/DevOps:
- [ ] Aktifkan Read Replica di Supabase untuk query analytics
- [ ] Jadwalkan ETL script mingguan/bulanan ke Data Warehouse
- [ ] Integrasi dengan BI tool (Metabase direkomendasikan karena open-source)
