from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

# Definisi ENUM di Python agar sesuai dengan PostgreSQL
class UserRole(str, enum.Enum):
    Admin = 'Admin'
    User = 'User'

class JenisKendaraan(str, enum.Enum):
    Mobil = 'Mobil'
    Motor = 'Motor'

class TipePlat(str, enum.Enum):
    Tipe_1 = '1'
    Tipe_2 = '2'
    Tipe_3 = '3'
    Tipe_4 = '4'
    Tipe_5 = '5'
    Tipe_6 = '6'
    Tipe_7 = '7'

class StatusGerak(str, enum.Enum):
    Masuk = 'Masuk'
    Keluar = 'Keluar'


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), unique=True, index=True, nullable=False)
    password = Column(String(30), nullable=False)
    role = Column(SQLEnum(UserRole, name="user_role_enum"), nullable=False)

class Personel(Base):
    __tablename__ = "personel"
    id_personel = Column(Integer, primary_key=True, index=True)
    nama_lengkap = Column(String(50), nullable=False)
    nip = Column(String(20), unique=True)
    pangkat = Column(String(30))
    jabatan = Column(String(50))
    fakultas = Column(String(50))
    
    kendaraan = relationship("Kendaraan", back_populates="personel")

class Kendaraan(Base):
    __tablename__ = "kendaraan"
    plat_nomor = Column(String(15), primary_key=True, index=True)
    id_personel = Column(Integer, ForeignKey("personel.id_personel", ondelete="SET NULL"), nullable=True)
    jenis_kendaraan = Column(SQLEnum(JenisKendaraan, name="jenis_kendaraan_enum"), nullable=False)
    tipe_plat = Column(SQLEnum('1', '2', '3', '4', '5', '6', '7', name="tipe_plat_enum"), nullable=False)
    
    personel = relationship("Personel", back_populates="kendaraan")
    log_akses = relationship("LogAkses", back_populates="kendaraan", cascade="all, delete-orphan")

class LogAkses(Base):
    __tablename__ = "log_akses"
    id_log = Column(Integer, primary_key=True, index=True)
    plat_nomor = Column(String(15), ForeignKey("kendaraan.plat_nomor", ondelete="CASCADE"), nullable=False, index=True)
    waktu_akses = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status_gerak = Column(SQLEnum(StatusGerak, name="status_gerak_enum"), nullable=False)
    
    kendaraan = relationship("Kendaraan", back_populates="log_akses")
