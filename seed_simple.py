import random
from sqlalchemy.orm import Session
from api.database import SessionLocal
from api.models import Admin, Personel, Kendaraan, LogAkses

def seed_data():
    db = SessionLocal()
    try:
        print("Mulai mengisi data dummy (CamelCase table)...")
        
        # 1. Buat Admin Dummy
        admin1 = Admin(namaAdmin="Budi Santoso", shiftJaga="Pagi")
        admin2 = Admin(namaAdmin="Ahmad Yani", shiftJaga="Malam")
        db.add_all([admin1, admin2])
        db.flush()

        # Daftar Fakultas Unhan RI
        fakultas_unhan = [
            "Fakultas Strategi Pertahanan",
            "Fakultas Manajemen Pertahanan",
            "Fakultas Keamanan Nasional",
            "Fakultas Sains dan Teknologi Pertahanan",
            "Fakultas Kedokteran dan Ilmu Kesehatan",
            "Fakultas Farmasi Militer",
            "Fakultas MIPA Militer"
        ]
        
        # Daftar Jabatan Unhan RI
        jabatan_unhan = [
            "Rektor", "Wakil Rektor", "Dekan", "Wakil Dekan", 
            "Kaprodi", "Dosen Tetap", "Peneliti", "Staf Akademik"
        ]

        # 2. Buat Personel Dummy
        personel_list = []
        for i in range(1, 6):
            p = Personel(
                namaLengkap=f"Personel {i}",
                nip=1000000000000000 + i,
                pangkat=random.choice(["Jenderal", "Kolonel", "Letkol", "Mayor", "Kapten", "Lettu"]),
                jabatan=random.choice(jabatan_unhan),
                fakultas=random.choice(fakultas_unhan)
            )
            personel_list.append(p)
            db.add(p)
        db.flush()

        # 3. Buat Kendaraan Dummy
        kendaraan_list = []
        for i, p in enumerate(personel_list):
            k = Kendaraan(
                platNomor=f"B 1{i}23 UN",
                nip=p.nip,
                jenisKendaraan="Mobil",
                instansi="Unhan RI"
            )
            kendaraan_list.append(k)
            db.add(k)
        
        # Tambah satu kendaraan tamu
        tamu = Kendaraan(
            platNomor="D 4444 TM",
            nip=None,
            jenisKendaraan="Mobil",
            instansi="Tamu"
        )
        kendaraan_list.append(tamu)
        db.add(tamu)
        db.flush()

        # 4. Buat LogAkses Dummy
        for k in kendaraan_list:
            log = LogAkses(
                platNomor=k.platNomor,
                idAdmin=admin1.idAdmin,
                jenisAkses="RFID",
                statusBuka=random.choice(["Masuk", "Keluar"]),
                instansi=k.instansi
            )
            db.add(log)
            
        db.commit()
        print("Berhasil mengisi data dummy dengan data Unhan RI!")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
