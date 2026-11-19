import enum
from datetime import date, datetime
from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class StatusPendaftaran(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class JalurMasuk(str, enum.Enum):
    SNBP = "SNBP"
    SNBT = "SNBT"
    MANDIRI = "Mandiri"


class ProgramStudi(Base):
    __tablename__ = "program_studi"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kode: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)
    fakultas: Mapped[str] = mapped_column(String(100), nullable=False)
    calon_mahasiswa: Mapped[list["CalonMahasiswa"]] = relationship(back_populates="program_studi")


class CalonMahasiswa(Base):
    __tablename__ = "calon_mahasiswa"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nama_lengkap: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(16), nullable=False)
    tanggal_lahir: Mapped[date] = mapped_column(Date, nullable=False)
    alamat: Mapped[str] = mapped_column(String(255), nullable=False)
    program_studi_id: Mapped[int] = mapped_column(ForeignKey("program_studi.id"), nullable=False)
    jalur_masuk: Mapped[JalurMasuk] = mapped_column(Enum(JalurMasuk), nullable=False)
    status: Mapped[StatusPendaftaran] = mapped_column(
        Enum(StatusPendaftaran), default=StatusPendaftaran.PENDING, nullable=False
    )
    nim: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    program_studi: Mapped[ProgramStudi] = relationship(back_populates="calon_mahasiswa")


class NIMCounter(Base):
    __tablename__ = "nim_counter"
    __table_args__ = (UniqueConstraint("tahun", "kode_prodi", name="uq_nim_counter"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tahun: Mapped[int] = mapped_column(Integer, nullable=False)
    kode_prodi: Mapped[str] = mapped_column(String(3), nullable=False)
    nomor_terakhir: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

