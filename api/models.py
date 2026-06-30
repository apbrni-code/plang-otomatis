from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Admin(Base):
    __tablename__ = "Admin"
    idAdmin = Column("idAdmin", Integer, primary_key=True, index=True)
    namaAdmin = Column("namaAdmin", String(50), nullable=True)
    shiftJaga = Column("shiftJaga", String(20), nullable=True)

class Personel(Base):
    __tablename__ = "Personel"
    idPersonel = Column("idPersonel", Integer, primary_key=True, index=True)
    nip = Column("nip", BigInteger, unique=True)
    namaLengkap = Column("namaLengkap", String(50), nullable=True)
    pangkat = Column("pangkat", String(50), nullable=True)
    jabatan = Column("jabatan", String(50), nullable=True)
    fakultas = Column("fakultas", String(50), nullable=True)
    
    kendaraan = relationship("Kendaraan", back_populates="personel")

class Kendaraan(Base):
    __tablename__ = "Kendaraan"
    platNomor = Column("platNomor", String(15), primary_key=True, index=True)
    nip = Column("nip", BigInteger, ForeignKey("Personel.nip", ondelete="CASCADE"), nullable=True)
    jenisKendaraan = Column("jenisKendaraan", String(30), nullable=True)
    tipePlat = Column("tipePlat", Integer, nullable=True)  # 1=TNI AD, 2=TNI AL, 3=TNI AU, 4=POLRI, 5=KEMHAN, 6=SIPIL
    instansi = Column("instansi", String(25), nullable=True)
    
    personel = relationship("Personel", back_populates="kendaraan")
    log_akses = relationship("LogAkses", back_populates="kendaraan", cascade="all, delete-orphan")

class LogAkses(Base):
    __tablename__ = "LogAkses"
    idLog = Column("idLog", Integer, primary_key=True, index=True)
    platNomor = Column("platNomor", String(15), ForeignKey("Kendaraan.platNomor", ondelete="CASCADE"), nullable=False, index=True)
    idAdmin = Column("idAdmin", Integer, ForeignKey("Admin.idAdmin", ondelete="SET NULL"), nullable=True)
    waktuAkses = Column("waktuAkses", DateTime(timezone=True), server_default=func.now(), nullable=False)
    jenisAkses = Column("jenisAkses", String(20), nullable=True)
    statusBuka = Column("statusBuka", String(20), nullable=True)
    instansi = Column("instansi", String(25), nullable=True)
    
    kendaraan = relationship("Kendaraan", back_populates="log_akses")
    admin = relationship("Admin")
