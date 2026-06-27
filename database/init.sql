-- ====================================================================
-- Database Schema
-- ====================================================================

-- 0. Drop existing tables
DROP TABLE IF EXISTS "LogAkses" CASCADE;
DROP TABLE IF EXISTS "Admin" CASCADE;
DROP TABLE IF EXISTS "Kendaraan" CASCADE;
DROP TABLE IF EXISTS "Personel" CASCADE;

-- Drop old lowercase tables just in case they are still there
DROP TABLE IF EXISTS logakses CASCADE;
DROP TABLE IF EXISTS admin CASCADE;
DROP TABLE IF EXISTS kendaraan CASCADE;
DROP TABLE IF EXISTS personel CASCADE;

-- Drop old types if they exist
DROP TYPE IF EXISTS user_role_enum CASCADE;
DROP TYPE IF EXISTS jenis_kendaraan_enum CASCADE;
DROP TYPE IF EXISTS tipe_plat_enum CASCADE;
DROP TYPE IF EXISTS status_gerak_enum CASCADE;

-- 1. Pembuatan Tabel

-- Tabel Personel
CREATE TABLE "Personel" (
    "idPersonel" SERIAL PRIMARY KEY,
    "nip" BIGINT UNIQUE,
    "namaLengkap" VARCHAR(50),
    "pangkat" VARCHAR(50),
    "jabatan" VARCHAR(50),
    "fakultas" VARCHAR(50)
);

-- Tabel Kendaraan
CREATE TABLE "Kendaraan" (
    "platNomor" VARCHAR(15) PRIMARY KEY,
    "nip" BIGINT REFERENCES "Personel"("nip") ON DELETE CASCADE,
    "jenisKendaraan" VARCHAR(30),
    "instansi" VARCHAR(25)
);

-- Tabel Admin
CREATE TABLE "Admin" (
    "idAdmin" SERIAL PRIMARY KEY,
    "namaAdmin" VARCHAR(50),
    "shiftJaga" VARCHAR(20)
);

-- Tabel LogAkses
CREATE TABLE "LogAkses" (
    "idLog" SERIAL PRIMARY KEY,
    "platNomor" VARCHAR(15) REFERENCES "Kendaraan"("platNomor") ON DELETE CASCADE,
    "idAdmin" INTEGER REFERENCES "Admin"("idAdmin") ON DELETE SET NULL,
    "waktuAkses" TIMESTAMP DEFAULT NOW(),
    "jenisAkses" VARCHAR(20),
    "statusBuka" VARCHAR(20),
    "instansi" VARCHAR(25)
);
