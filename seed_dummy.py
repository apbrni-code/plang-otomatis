import os
import re
from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy import text as sql_text
from api.database import engine, SessionLocal
from api import models

fake = Faker('id_ID')

DATA_DIR = os.path.join("DATA plat", "Dataset_Primer_Raw")

def clean_plate(text):
    cleaned = re.sub(r'[^A-Z0-9\- ]', '', text.upper())
    return cleaned.strip()

def generate_dummy_personel(db: Session):
    pangkat_list = ["Jenderal", "Kolonel", "Letkol", "Mayor", "Kapten", "Lettu"]
    
    jabatan_unhan = [
        "Rektor", "Wakil Rektor", "Dekan", "Wakil Dekan", 
        "Kaprodi", "Dosen Tetap", "Peneliti", "Staf Akademik"
    ]
    
    fakultas_unhan = [
        "Fakultas Strategi Pertahanan",
        "Fakultas Manajemen Pertahanan",
        "Fakultas Keamanan Nasional",
        "Fakultas Sains dan Teknologi Pertahanan",
        "Fakultas Kedokteran dan Ilmu Kesehatan",
        "Fakultas Farmasi Militer",
        "Fakultas MIPA Militer"
    ]
    
    # NIP is BigInteger, so we use digits
    new_personel = models.Personel(
        namaLengkap=fake.name()[:50],
        nip=int(fake.numerify('##################')[:18]),
        pangkat=fake.random_element(elements=pangkat_list),
        jabatan=fake.random_element(elements=jabatan_unhan),
        fakultas=fake.random_element(elements=fakultas_unhan)
    )
    db.add(new_personel)
    db.flush()
    return new_personel

def process_images():
    print("Mulai membaca data primer...")
    db = SessionLocal()
    seen_plates = set()
    try:
        # Bersihkan tabel secara tuntas dan reset ID ke angka 1
        print("Mereset tabel dan ID ke 1...")
        db.execute(sql_text('TRUNCATE TABLE "LogAkses", "Kendaraan", "Personel", "Admin" RESTART IDENTITY CASCADE;'))
        db.commit()
        
        # Buat Admin Dummy
        admin_dummy = models.Admin(namaAdmin="Admin Dummy", shiftJaga="Pagi")
        db.add(admin_dummy)
        db.flush()
        
        if not os.path.exists(DATA_DIR):
            print(f"Directory {DATA_DIR} tidak ditemukan, seeding dibatalkan.")
            return

        for folder_name in os.listdir(DATA_DIR):
            folder_path = os.path.join(DATA_DIR, folder_name)
            if not os.path.isdir(folder_path):
                continue
            
            print(f"\\nMembaca folder: {folder_name}")
            
            for file_name in os.listdir(folder_path):
                if file_name.lower().endswith(('.jpg', '.png', '.jpeg')):
                    print(f"  -> Memproses: {file_name}")
                    
                    # Ambil nama file tanpa ekstensi sebagai nomor plat
                    raw_plate = os.path.splitext(file_name)[0]
                    plate_text = clean_plate(raw_plate)
                    
                    if not plate_text or len(plate_text) < 3:
                        print(f"     [SKIP] Nama file tidak valid untuk plat: {file_name}")
                        continue
                        
                    plate_text = plate_text[:15]
                    print(f"     [OK] Plat didapat dari nama file: {plate_text}")
                    
                    if plate_text in seen_plates:
                        continue
                        
                    existing = db.query(models.Kendaraan).filter(models.Kendaraan.platNomor == plate_text).first()
                    if existing:
                        continue
                    
                    seen_plates.add(plate_text)
                    
                    personel = generate_dummy_personel(db)
                    
                    instansi_kendaraan = folder_name
                    
                    new_kendaraan = models.Kendaraan(
                        platNomor=plate_text,
                        nip=personel.nip,
                        jenisKendaraan="Mobil",
                        instansi=instansi_kendaraan
                    )
                    db.add(new_kendaraan)
                    
                    log_masuk = models.LogAkses(
                        platNomor=plate_text,
                        idAdmin=admin_dummy.idAdmin,
                        jenisAkses="RFID",
                        statusBuka="Masuk",
                        instansi=instansi_kendaraan
                    )
                    db.add(log_masuk)
                    
        # --- Proses Data Sekunder (Sipil) ---
        SEKUNDER_DIR = os.path.join("DATA plat", "Dataset_Sekunder_Visitor", "train", "images")
        if os.path.exists(SEKUNDER_DIR):
            import random
            print(f"\nMembaca data sekunder (Sipil) dari folder: train/images")
            count_sipil = 0
            for file_name in os.listdir(SEKUNDER_DIR):
                if file_name.lower().endswith(('.jpg', '.png', '.jpeg')):
                    match = re.search(r'([A-Z]{1,2})(-[0-9]{1,4}-[A-Z]{1,3})', file_name)
                    if match:
                        prefix = match.group(1)
                        suffix = match.group(2)
                        
                        # Ubah plat 'E' menjadi 'B' atau 'F' secara acak
                        if prefix == 'E':
                            prefix = random.choice(['B', 'F'])
                            
                        raw_plate = prefix + suffix
                        plate_text = clean_plate(raw_plate)
                        
                        if plate_text in seen_plates:
                            continue
                            
                        existing = db.query(models.Kendaraan).filter(models.Kendaraan.platNomor == plate_text).first()
                        if existing:
                            continue
                        
                        seen_plates.add(plate_text)
                        
                        if count_sipil < 5: # Batasi log agar tidak terlalu panjang
                            print(f"  -> Memproses (Sipil): {file_name}")
                            print(f"     [OK] Plat didapat: {plate_text}")
                        elif count_sipil == 5:
                            print("  -> ... (menyembunyikan log lainnya agar rapi) ...")
                            
                        count_sipil += 1
                        
                        personel = generate_dummy_personel(db)
                        instansi_kendaraan = "Sipil"
                        
                        new_kendaraan = models.Kendaraan(
                            platNomor=plate_text,
                            nip=personel.nip,
                            jenisKendaraan="Mobil",
                            instansi=instansi_kendaraan
                        )
                        db.add(new_kendaraan)
                        
                        log_masuk = models.LogAkses(
                            platNomor=plate_text,
                            idAdmin=admin_dummy.idAdmin,
                            jenisAkses="RFID",
                            statusBuka="Masuk",
                            instansi=instansi_kendaraan
                        )
                        db.add(log_masuk)
            print(f"Berhasil menambahkan {count_sipil} data Sipil.")
        # ------------------------------------
                    
        db.commit()
        print("\\nSelesai! Semua data telah di-insert ke database dengan ID dimulai dari 1.")
    except Exception as e:
        db.rollback()
        print(f"Terjadi error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    process_images()
