import enum
from datetime import time, datetime
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class KRSStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REVISION = "REVISION"


class MataKuliah(Base):
    __tablename__ = "matakuliah"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kode_mk: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    nama_mk: Mapped[str] = mapped_column(String(120), nullable=False)
    sks: Mapped[int] = mapped_column(Integer, nullable=False)
    schedules: Mapped[list["JadwalKuliah"]] = relationship(back_populates="mata_kuliah")


class JadwalKuliah(Base):
    __tablename__ = "jadwal_kuliah"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mata_kuliah_id: Mapped[int] = mapped_column(ForeignKey("matakuliah.id"), nullable=False)
    hari: Mapped[str] = mapped_column(String(12), nullable=False)
    jam_mulai: Mapped[time] = mapped_column(Time, nullable=False)
    jam_selesai: Mapped[time] = mapped_column(Time, nullable=False)
    ruangan_id: Mapped[int | None] = mapped_column(ForeignKey("ruangan.id"), nullable=True)
    dosen_id: Mapped[str | None] = mapped_column(String(30), nullable=True)
    jumlah_mahasiswa: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mata_kuliah: Mapped[MataKuliah] = relationship(back_populates="schedules")
    ruangan: Mapped["Ruangan | None"] = relationship(back_populates="jadwal")


class Ruangan(Base):
    __tablename__ = "ruangan"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kode_ruang: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    kapasitas: Mapped[int] = mapped_column(Integer, nullable=False)
    jadwal: Mapped[list[JadwalKuliah]] = relationship(back_populates="ruangan")


class Prerequisite(Base):
    __tablename__ = "prerequisite"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mata_kuliah_id: Mapped[int] = mapped_column(ForeignKey("matakuliah.id"), nullable=False)
    prerequisite_id: Mapped[int] = mapped_column(ForeignKey("matakuliah.id"), nullable=False)
    __table_args__ = (UniqueConstraint("mata_kuliah_id", "prerequisite_id", name="uq_prerequisite"),)


class AcademicRecord(Base):
    __tablename__ = "academic_record"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nim: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    mata_kuliah_id: Mapped[int] = mapped_column(ForeignKey("matakuliah.id"), nullable=False)
    nilai_huruf: Mapped[str] = mapped_column(String(2), nullable=False)
    semester: Mapped[str] = mapped_column(String(12), nullable=False)
    __table_args__ = (UniqueConstraint("nim", "mata_kuliah_id", "semester", name="uq_record"),)


class Grade(Base):
    __tablename__ = "grades"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nim: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    mata_kuliah_id: Mapped[int] = mapped_column(ForeignKey("matakuliah.id"), nullable=False)
    semester: Mapped[str] = mapped_column(String(12), nullable=False)
    nilai_huruf: Mapped[str] = mapped_column(String(2), nullable=False)
    nilai_angka: Mapped[float] = mapped_column(nullable=False)
    attendance_percent: Mapped[float] = mapped_column(nullable=False)
    input_by: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    mata_kuliah: Mapped[MataKuliah] = relationship()
    histories: Mapped[list["GradeHistory"]] = relationship(back_populates="grade", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("nim", "mata_kuliah_id", "semester", name="uq_grade_per_course_semester"),)


class GradeHistory(Base):
    __tablename__ = "grade_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.id"), nullable=False)
    old_value: Mapped[str] = mapped_column(String(2), nullable=False)
    new_value: Mapped[str] = mapped_column(String(2), nullable=False)
    changed_by: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    grade: Mapped[Grade] = relationship(back_populates="histories")


class KRS(Base):
    __tablename__ = "krs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nim: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    semester: Mapped[str] = mapped_column(String(12), nullable=False)
    status: Mapped[KRSStatus] = mapped_column(Enum(KRSStatus), default=KRSStatus.DRAFT, nullable=False)
    dosen_pa_id: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    details: Mapped[list["KRSDetail"]] = relationship(back_populates="krs", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("nim", "semester", name="uq_krs_per_semester"),)


class KRSDetail(Base):
    __tablename__ = "krs_detail"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    krs_id: Mapped[int] = mapped_column(ForeignKey("krs.id"), nullable=False)
    mata_kuliah_id: Mapped[int] = mapped_column(ForeignKey("matakuliah.id"), nullable=False)
    krs: Mapped[KRS] = relationship(back_populates="details")
    mata_kuliah: Mapped[MataKuliah] = relationship()
    __table_args__ = (UniqueConstraint("krs_id", "mata_kuliah_id", name="uq_krs_course"),)

