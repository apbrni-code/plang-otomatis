from pydantic import BaseModel, constr
from datetime import datetime
from typing import Optional

# Skema untuk request payload dari Kamera/OCR
class OCRPayload(BaseModel):
    platNomor: constr(max_length=15) # type: ignore
    jenisAkses: Optional[str] = None
    statusBuka: Optional[str] = None
    instansi: Optional[str] = None
    confidence_score: float = 0.0 # Boleh ada tambahan metadata dari OCR
    
    class Config:
        from_attributes = True

# Skema Response
class LogAksesResponse(BaseModel):
    idLog: int
    platNomor: str
    idAdmin: Optional[int]
    jenisAkses: Optional[str]
    statusBuka: Optional[str]
    instansi: Optional[str]
    waktuAkses: datetime
    
    class Config:
        from_attributes = True
