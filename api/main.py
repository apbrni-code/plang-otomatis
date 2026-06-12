from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import time

from . import models, schemas
from .database import engine, get_db

# (Opsional) Buat tabel secara otomatis saat startup (jika belum ada)
# Dalam produksi, sebaiknya jalankan ini via script terpisah atau biarkan Supabase yang mengurusnya.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Data Pipeline Unhan RI",
    description="API untuk menerima log kendaraan dari sistem OCR gerbang kampus.",
    version="1.0.0"
)

# Background Task untuk asinkronus insert database agar API super cepat
def process_ocr_data(payload: schemas.OCRPayload, db: Session):
    # 1. Cek apakah kendaraan sudah terdaftar
    kendaraan = db.query(models.Kendaraan).filter(models.Kendaraan.plat_nomor == payload.plat_nomor).first()
    
    # 2. Jika tidak terdaftar (Tamu/Salah Baca), insert kendaraan dummy dulu
    # untuk menghindari Foreign Key error di LogAkses
    if not kendaraan:
        # Default sebagai kendaraan Tamu
        new_kendaraan = models.Kendaraan(
            plat_nomor=payload.plat_nomor,
            jenis_kendaraan=models.JenisKendaraan.Mobil, # Default tebakan
            tipe_plat=models.TipePlat.Tipe_1
        )
        db.add(new_kendaraan)
        try:
            db.commit()
            db.refresh(new_kendaraan)
        except Exception as e:
            db.rollback()
            print(f"Error insert kendaraan baru: {e}")
            return
            
    # 3. Masukkan ke Log Akses
    log_baru = models.LogAkses(
        plat_nomor=payload.plat_nomor,
        status_gerak=payload.status_gerak
    )
    db.add(log_baru)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error insert log akses: {e}")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API Pipeline Unhan RI Berjalan"}

@app.post("/api/v1/ocr-ingest", status_code=202)
def ingest_ocr(
    payload: schemas.OCRPayload, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    """
    Endpoint yang dipanggil oleh kamera/OCR saat mobil lewat.
    Menggunakan BackgroundTasks agar respons HTTP instan (mencegah bottleneck).
    """
    # Lempar pemrosesan database ke background
    background_tasks.add_task(process_ocr_data, payload, db)
    
    return {
        "status": "accepted", 
        "plat_nomor": payload.plat_nomor,
        "message": "Data sedang diproses di background."
    }

@app.get("/api/v1/logs")
def get_logs(db: Session = Depends(get_db), limit: int = 10):
    """
    Endpoint untuk melihat data log kendaraan yang sudah terekam.
    """
    logs = db.query(models.LogAkses).order_by(models.LogAkses.waktu_akses.desc()).limit(limit).all()
    return {"data": logs}

@app.get("/api/v1/kendaraan")
def get_kendaraan(db: Session = Depends(get_db)):
    """
    Endpoint untuk melihat daftar kendaraan yang terdaftar di database.
    """
    kendaraan = db.query(models.Kendaraan).all()
    return {"data": kendaraan}

@app.get("/api/v1/analytics/daily-traffic")
def get_daily_traffic(db: Session = Depends(get_db)):
    """
    Endpoint untuk analitik: Menghitung statistik traffic kendaraan (contoh dashboard).
    """
    from datetime import date
    
    # Menghitung total masuk
    masuk = db.query(models.LogAkses).filter(
        models.LogAkses.status_gerak == models.StatusGerak.Masuk
    ).count()
    
    # Menghitung total keluar
    keluar = db.query(models.LogAkses).filter(
        models.LogAkses.status_gerak == models.StatusGerak.Keluar
    ).count()
    
    return {
        "report_date": str(date.today()),
        "total_masuk": masuk,
        "total_keluar": keluar,
        "total_kendaraan_terdaftar": db.query(models.Kendaraan).count()
    }
