from pydantic import BaseModel, constr
from datetime import datetime
from typing import Optional

# Mapping kode tipe plat dari output model → label string
TIPE_PLAT_MAP: dict[int, str] = {
    1: "TNI AD",
    2: "TNI AL",
    3: "TNI AU",
    4: "POLRI",
    5: "KEMHAN",
    6: "SIPIL",
}

# Skema untuk request payload dari Kamera/OCR
class OCRPayload(BaseModel):
    platNomor: constr(max_length=15) # type: ignore
    tipePlat: Optional[int] = None   # Kode tipe plat dari model: 1=TNI AD, 2=TNI AL, 3=TNI AU, 4=POLRI, 5=KEMHAN, 6=SIPIL
    jenisAkses: Optional[str] = None
    statusBuka: Optional[str] = None
    instansi: Optional[str] = None
    confidence_score: float = 0.0   # Confidence score dari model OCR
    
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
