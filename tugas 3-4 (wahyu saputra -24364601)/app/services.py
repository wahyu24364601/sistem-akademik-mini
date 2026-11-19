from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .models import CalonMahasiswa, NIMCounter, ProgramStudi, StatusPendaftaran
from .schemas import RegisterRequest


def register_applicant(db: Session, payload: RegisterRequest) -> CalonMahasiswa:
    if db.scalar(select(CalonMahasiswa).where(CalonMahasiswa.email == str(payload.email))):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email sudah terdaftar")
    if not db.get(ProgramStudi, payload.program_studi_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program studi tidak ditemukan")
    applicant_data = payload.model_dump()
    applicant_data["email"] = str(payload.email)
    applicant = CalonMahasiswa(**applicant_data)
    db.add(applicant)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email sudah terdaftar")
    db.refresh(applicant)
    return applicant


def generate_nim(db: Session, applicant: CalonMahasiswa) -> str:
    """SQLite uses BEGIN IMMEDIATE so two approvals cannot reserve the same sequence."""
    if applicant.nim:
        return applicant.nim
    prodi = db.get(ProgramStudi, applicant.program_studi_id)
    tahun = datetime.now().year
    db.execute(text("BEGIN IMMEDIATE"))
    counter = db.scalar(
        select(NIMCounter).where(NIMCounter.tahun == tahun, NIMCounter.kode_prodi == prodi.kode)
    )
    if counter is None:
        counter = NIMCounter(tahun=tahun, kode_prodi=prodi.kode, nomor_terakhir=0)
        db.add(counter)
        db.flush()
    counter.nomor_terakhir += 1
    return f"{tahun}{prodi.kode}-{counter.nomor_terakhir:04d}"


def approve_applicant(db: Session, applicant_id: int) -> CalonMahasiswa:
    applicant = db.get(CalonMahasiswa, applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pendaftar tidak ditemukan")
    if applicant.status == StatusPendaftaran.APPROVED:
        return applicant
    # End the read transaction before acquiring SQLite's write lock.
    db.commit()
    try:
        applicant.nim = generate_nim(db, applicant)
        applicant.status = StatusPendaftaran.APPROVED
        applicant.approved_at = datetime.utcnow()
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Gagal menghasilkan NIM unik")
    db.refresh(applicant)
    return applicant

