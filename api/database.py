import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load variabel dari file .env
load_dotenv()

# Konfigurasi Koneksi Database
# Mengambil dari file .env yang baru saja dibuat
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./unhan_pipeline.db"
)

# Buat Engine SQLAlchemy
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, pool_pre_ping=True
    )

# Pembuat Sesi Database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class untuk Model
Base = declarative_base()

# Dependency untuk digunakan di endpoint FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
