-- ====================================================================
-- Database Schema untuk Sistem Plang Unhan RI (Supabase/PostgreSQL)
-- ====================================================================

-- 0. Drop existing tables and types (Untuk memudahkan re-run script)
DROP TABLE IF EXISTS Log_Akses CASCADE;
DROP TABLE IF EXISTS Kendaraan CASCADE;
DROP TABLE IF EXISTS Personel CASCADE;
DROP TABLE IF EXISTS "users" CASCADE;

DROP TYPE IF EXISTS user_role_enum CASCADE;
DROP TYPE IF EXISTS jenis_kendaraan_enum CASCADE;
DROP TYPE IF EXISTS tipe_plat_enum CASCADE;
DROP TYPE IF EXISTS status_gerak_enum CASCADE;

-- 1. Definisi Tipe Data ENUM
CREATE TYPE user_role_enum AS ENUM ('Admin', 'User');
CREATE TYPE jenis_kendaraan_enum AS ENUM ('Mobil', 'Motor');
CREATE TYPE tipe_plat_enum AS ENUM ('1', '2', '3', '4', '5', '6', '7');
CREATE TYPE status_gerak_enum AS ENUM ('Masuk', 'Keluar');

-- 2. Pembuatan Tabel

-- Tabel User
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(30) UNIQUE NOT NULL,
    password VARCHAR(30) NOT NULL,
    role user_role_enum NOT NULL
);

-- Tabel Personel
CREATE TABLE personel (
    id_personel SERIAL PRIMARY KEY,
    nama_lengkap VARCHAR(50) NOT NULL,
    nip VARCHAR(20) UNIQUE,
    pangkat VARCHAR(30),
    jabatan VARCHAR(50),
    fakultas VARCHAR(50)
);

-- Tabel Kendaraan
CREATE TABLE kendaraan (
    plat_nomor VARCHAR(15) PRIMARY KEY,
    id_personel INTEGER REFERENCES personel(id_personel) ON DELETE SET NULL,
    jenis_kendaraan jenis_kendaraan_enum NOT NULL,
    tipe_plat tipe_plat_enum NOT NULL
);

-- Tabel Log Akses
CREATE TABLE log_akses (
    id_log SERIAL PRIMARY KEY,
    plat_nomor VARCHAR(15) REFERENCES kendaraan(plat_nomor) ON DELETE CASCADE,
    waktu_akses TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    status_gerak status_gerak_enum NOT NULL
);

-- 3. Pembuatan Indexes untuk Performa
CREATE INDEX idx_log_plat_nomor ON log_akses(plat_nomor);
CREATE INDEX idx_log_waktu_akses ON log_akses USING BRIN (waktu_akses);

-- 4. Setup Realtime Supabase (Opsional tapi direkomendasikan)
-- Menambahkan tabel log_akses ke publikasi realtime agar dashboard satpam bisa update otomatis
ALTER PUBLICATION supabase_realtime ADD TABLE log_akses;
