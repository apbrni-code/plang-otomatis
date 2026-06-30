from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import time

from . import models, schemas
from .database import engine, get_db
from .schemas import TIPE_PLAT_MAP

app = FastAPI(
    title="Data Pipeline Unhan RI",
    description="API untuk menerima log kendaraan dari sistem OCR gerbang kampus.",
    version="1.0.0"
)

def process_ocr_data(payload: schemas.OCRPayload, db: Session):
    # Resolve label instansi dari kode tipePlat model
    label_instansi = TIPE_PLAT_MAP.get(payload.tipePlat, "Tamu") if payload.tipePlat else (payload.instansi or "Tamu")
    
    # 1. Cek apakah kendaraan sudah terdaftar
    kendaraan = db.query(models.Kendaraan).filter(models.Kendaraan.platNomor == payload.platNomor).first()
    
    # 2. Jika tidak terdaftar (Tamu/Salah Baca), insert kendaraan dummy dulu
    if not kendaraan:
        new_kendaraan = models.Kendaraan(
            platNomor=payload.platNomor,
            jenisKendaraan="Mobil",       # Default tebakan
            tipePlat=payload.tipePlat,    # Kode dari model (bisa None jika tidak terdeteksi)
            instansi=label_instansi       # Label otomatis dari TIPE_PLAT_MAP
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
        platNomor=payload.platNomor,
        jenisAkses=payload.jenisAkses,
        statusBuka=payload.statusBuka,
        instansi=label_instansi           # Label yang sama untuk konsistensi log
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
    background_tasks.add_task(process_ocr_data, payload, db)
    
    return {
        "status": "accepted", 
        "platNomor": payload.platNomor,
        "message": "Data sedang diproses di background."
    }

@app.get("/api/v1/logs")
def get_logs(db: Session = Depends(get_db), limit: int = 10):
    logs = db.query(models.LogAkses).order_by(models.LogAkses.waktuAkses.desc()).limit(limit).all()
    return {"data": logs}

@app.get("/api/v1/kendaraan")
def get_kendaraan(db: Session = Depends(get_db)):
    kendaraan = db.query(models.Kendaraan).all()
    return {"data": kendaraan}

@app.get("/api/v1/analytics/daily-traffic")
def get_daily_traffic(db: Session = Depends(get_db)):
    from datetime import date
    
    masuk = db.query(models.LogAkses).filter(
        models.LogAkses.statusBuka == "Masuk"
    ).count()
    
    keluar = db.query(models.LogAkses).filter(
        models.LogAkses.statusBuka == "Keluar"
    ).count()
    
    return {
        "report_date": str(date.today()),
        "total_masuk": masuk,
        "total_keluar": keluar,
        "total_kendaraan_terdaftar": db.query(models.Kendaraan).count()
    }
