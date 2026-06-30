# Entity Relationship Diagram (ERD) - Data Pipeline Unhan RI

Berikut adalah desain skema database relasional (ERD) berdasarkan struktur tabel yang saat ini berjalan di sistem.

```mermaid
erDiagram
    Admin {
        int idAdmin PK
        varchar(50) namaAdmin
        varchar(20) shiftJaga
    }

    Personel {
        int idPersonel PK
        bigint nip "UNIQUE"
        varchar(50) namaLengkap
        varchar(50) pangkat
        varchar(50) jabatan
        varchar(50) fakultas
    }

    Kendaraan {
        varchar(15) platNomor PK
        bigint nip FK
        varchar(30) jenisKendaraan
        int tipePlat "1=TNI AD, 2=TNI AL, 3=TNI AU, 4=POLRI, 5=KEMHAN, 6=SIPIL"
        varchar(25) instansi
    }

    LogAkses {
        int idLog PK
        varchar(15) platNomor FK
        int idAdmin FK
        timestamp waktuAkses "DEFAULT NOW()"
        varchar(20) jenisAkses
        varchar(20) statusBuka
        varchar(25) instansi
    }

    %% Relationships
    Personel ||--o{ Kendaraan : "memiliki"
    Kendaraan ||--o{ LogAkses : "tercatat di"
    Admin ||--o{ LogAkses : "mencatat"
```

### Keterangan Tabel:
1. **Admin**: Tabel untuk menyimpan data admin/petugas jaga.
2. **Personel**: Menyimpan data master para pegawai/dosen/militer di lingkungan Unhan. Berelasi ke tabel kendaraan menggunakan `nip`.
3. **Kendaraan**: Data kendaraan yang didaftarkan. Menggunakan `platNomor` sebagai Primary Key. Menyimpan kode `tipePlat` hasil dari klasifikasi OCR.
4. **LogAkses**: Tabel *transactional* yang akan memiliki volume data paling besar. Setiap kali kamera mendeteksi plat, satu *row* akan ditambahkan di sini. Menyimpan informasi akses, status pintu gerbang, dan instansi.
