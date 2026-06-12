import os
import re
import cv2
import easyocr
from faker import Faker
from sqlalchemy.orm import Session
from api.database import engine, SessionLocal
from api import models

# Inisialisasi
fake = Faker('id_ID')
reader = easyocr.Reader(['en']) # Model bahasa inggris cukup untuk baca plat nomor (alfanumerik)

DATA_DIR = os.path.join("DATA plat", "Dataset_Primer_Raw")

# Mapping nama folder ke enum TipePlat
# Tipe_1: Sipil, Tipe_2: TNI AD, Tipe_3: TNI AL, Tipe_4: TNI AU, Tipe_5: Polri, Tipe_6: Kemhan
# Karena di init.sql kita set TipePlat ke '1', '2', dll.
FOLDER_TO_TIPE = {
    "TNI AD": "2",
    "TNI AL": "3",
    "TNI AU": "4",
    "POLRI": "5",
    "Kemhan": "6",
    "PATI": "7",
    "Sipil": "1"
}

def clean_plate(text):
    # Biarkan huruf, angka, spasi, dan tanda hubung (karena plat militer sering pakai tanda hubung)
    cleaned = re.sub(r'[^A-Z0-9\- ]', '', text.upper())
    return cleaned.strip()

def generate_dummy_personel(db: Session, tipe_plat: str):
    # Buat personel dummy
    # Gunakan gelar/pangkat palsu
    pangkat_list = ["Kolonel", "Letkol", "Mayor", "Kapten", "Lettu", "Jenderal"]
    jabatan_list = ["Dosen", "Dekan", "Staf Akademik", "Peneliti", "Kajur"]
    fakultas_list = ["Fakultas Teknik Militer", "Fakultas Keamanan Nasional", "Fakultas Kedokteran Militer"]
    
    new_personel = models.Personel(
        nama_lengkap=fake.name()[:50], # Max 50 chars
        nip=fake.numerify('##################')[:20], # 18 digits NIP
        pangkat=fake.random_element(elements=pangkat_list),
        jabatan=fake.random_element(elements=jabatan_list),
        fakultas=fake.random_element(elements=fakultas_list)
    )
    db.add(new_personel)
    db.flush() # flush agar kita dapat id_personel
    return new_personel

def process_images():
    print("Mulai membaca data primer...")
    db = SessionLocal()
    seen_plates = set()
    try:
        for folder_name in os.listdir(DATA_DIR):
            folder_path = os.path.join(DATA_DIR, folder_name)
            if not os.path.isdir(folder_path):
                continue
            
            # Tentukan tipe plat
            tipe = FOLDER_TO_TIPE.get(folder_name, "1") # Default 1 (Sipil)
            
            print(f"\\nMembaca folder: {folder_name} (Tipe Plat: {tipe})")
            
            for file_name in os.listdir(folder_path):
                if file_name.lower().endswith(('.jpg', '.png', '.jpeg')):
                    img_path = os.path.join(folder_path, file_name)
                    print(f"  -> Memproses: {file_name}")
                    
                    # 1. Extract text via EasyOCR
                    # Baca gambar dengan OpenCV dan kecilkan ukurannya jika terlalu besar (mencegah Out of Memory)
                    img = cv2.imread(img_path)
                    if img is None:
                        print("     [!] Gagal membaca file gambar")
                        continue
                        
                    max_dimension = 1024
                    height, width = img.shape[:2]
                    if width > max_dimension or height > max_dimension:
                        scale = max_dimension / max(width, height)
                        img = cv2.resize(img, (int(width * scale), int(height * scale)))

                    result = reader.readtext(img)
                    
                    # Ambil teks terpanjang yang kemungkinan besar adalah plat nomor dan WAJIB mengandung angka
                    plate_text = ""
                    for bbox, text, prob in result:
                        cleaned_text = clean_plate(text)
                        
                        # Filter cerdas: Plat nomor PASTI mengandung angka. 
                        # Ini membuang teks seperti "ISUZU", "TOYOTA", dll.
                        if any(char.isdigit() for char in cleaned_text):
                            if len(cleaned_text) > len(plate_text) and len(cleaned_text) >= 3:
                                plate_text = cleaned_text
                    
                    if not plate_text:
                        print(f"     [!] Plat tidak terdeteksi")
                        continue
                        
                    # Potong jika lebih dari 15 karakter (limit database)
                    plate_text = plate_text[:15]
                    print(f"     [OK] Plat terbaca: {plate_text}")
                    
                    # 2. Cek apakah plat sudah ada di db atau di sesi ini
                    if plate_text in seen_plates:
                        print(f"     [SKIP] Plat sudah diproses di sesi ini")
                        continue
                        
                    existing = db.query(models.Kendaraan).filter(models.Kendaraan.plat_nomor == plate_text).first()
                    if existing:
                        print(f"     [SKIP] Plat sudah ada di database")
                        continue
                    
                    seen_plates.add(plate_text)
                    
                    # 3. Buat Dummy Personel
                    personel = generate_dummy_personel(db, tipe)
                    
                    # 4. Buat Kendaraan
                    new_kendaraan = models.Kendaraan(
                        plat_nomor=plate_text,
                        id_personel=personel.id_personel, # Ini ID-nya
                        jenis_kendaraan="Mobil", # Asumsi Mobil
                        tipe_plat=tipe
                    )
                    db.add(new_kendaraan)
                    
                    # Optional: Langsung buat Log Masuk hari ini
                    log_masuk = models.LogAkses(
                        plat_nomor=plate_text,
                        status_gerak="Masuk"
                    )
                    db.add(log_masuk)
                    
                    # Bersihkan memori RAM agar tidak kepenuhan
                    del img
                    del result
                    import gc
                    gc.collect()
                    
        db.commit()
        print("\\nSelesai! Semua data telah di-insert ke database.")
    except Exception as e:
        db.rollback()
        print(f"Terjadi error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    process_images()
