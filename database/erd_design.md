# Entity Relationship Diagram (ERD) - Data Pipeline Unhan RI

Berikut adalah desain skema database relasional (ERD) berdasarkan struktur tabel yang saat ini berjalan di sistem.

```mermaid
erDiagram
    USERS {
        int id PK
        varchar(30) username "UNIQUE"
        varchar(30) password
        enum role "Admin / User"
    }

    PERSONEL {
        int id_personel PK
        varchar(50) nama_lengkap
        varchar(20) nip "UNIQUE"
        varchar(30) pangkat
        varchar(50) jabatan
        varchar(50) fakultas
    }

    KENDARAAN {
        varchar(15) plat_nomor PK
        int id_personel FK
        enum jenis_kendaraan "Mobil / Motor"
        enum tipe_plat "1 s.d. 7"
    }

    LOG_AKSES {
        int id_log PK
        varchar(15) plat_nomor FK
        timestamp waktu_akses "DEFAULT NOW()"
        enum status_gerak "Masuk / Keluar"
    }

    %% Relationships
    PERSONEL ||--o{ KENDARAAN : "memiliki"
    KENDARAAN ||--o{ LOG_AKSES : "tercatat di"
```

### Keterangan Tabel:
1. **USERS**: Tabel *standalone* untuk menyimpan kredensial login akun admin atau pengguna dasbor.
2. **PERSONEL**: Menyimpan data master para pegawai/dosen/militer di lingkungan Unhan. Satu personel dapat memiliki lebih dari satu kendaraan (1 to Many).
3. **KENDARAAN**: Data kendaraan yang didaftarkan. Menggunakan `plat_nomor` sebagai Primary Key.
4. **LOG_AKSES**: Tabel *transactional* yang akan memiliki volume data paling besar. Setiap kali kamera mendeteksi plat, satu *row* akan ditambahkan di sini. Tabel ini berelasi dengan tabel KENDARAAN (1 to Many).
