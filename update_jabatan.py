import random
from sqlalchemy.orm import Session
from api.database import SessionLocal
from api.models import Personel

def update_personel_data():
    db = SessionLocal()
    try:
        print("Memperbarui jabatan dan fakultas ke data Unhan RI...")
        
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
        
        semua_personel = db.query(Personel).all()
        for p in semua_personel:
            p.jabatan = random.choice(jabatan_unhan)
            p.fakultas = random.choice(fakultas_unhan)
            p.pangkat = random.choice(pangkat_list)
            
        db.commit()
        print(f"Berhasil memperbarui {len(semua_personel)} personel!")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_personel_data()
