from pydantic import BaseModel, constr
from datetime import datetime
from typing import Optional
from .models import StatusGerak

# Skema untuk request payload dari Kamera/OCR
class OCRPayload(BaseModel):
    plat_nomor: constr(max_length=15) # type: ignore
    status_gerak: StatusGerak
    confidence_score: float = 0.0 # Boleh ada tambahan metadata dari OCR
    
    class Config:
        from_attributes = True

# Skema Response
class LogAksesResponse(BaseModel):
    id_log: int
    plat_nomor: str
    status_gerak: StatusGerak
    waktu_akses: datetime
    
    class Config:
        from_attributes = True
