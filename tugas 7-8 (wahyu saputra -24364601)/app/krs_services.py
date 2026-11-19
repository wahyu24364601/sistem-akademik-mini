from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from .models import CalonMahasiswa, StatusPendaftaran
from .krs_models import KRS, KRSDetail, KRSStatus, MataKuliah
from .krs_validators import build_validation_chain


def find_student(db: Session, nim: str):
    student = db.scalar(select(CalonMahasiswa).where(CalonMahasiswa.nim == nim))
    if not student or student.status != StatusPendaftaran.APPROVED:
        raise HTTPException(404, "Mahasiswa dengan NIM tersebut tidak ditemukan")
    return student


def get_or_create_krs(db: Session, nim: str, semester: str) -> KRS:
    find_student(db, nim)
    krs = db.scalar(select(KRS).where(KRS.nim == nim, KRS.semester == semester))
    if not krs:
        krs = KRS(nim=nim, semester=semester)
        db.add(krs); db.commit(); db.refresh(krs)
    return load_krs(db, krs.id)


def load_krs(db: Session, krs_id: int) -> KRS:
    return db.scalar(select(KRS).options(
        selectinload(KRS.details).selectinload(KRSDetail.mata_kuliah).selectinload(MataKuliah.schedules)
    ).where(KRS.id == krs_id))


def ensure_editable(krs: KRS):
    if krs.status not in (KRSStatus.DRAFT, KRSStatus.REVISION):
        raise HTTPException(400, "KRS hanya dapat diubah saat berstatus DRAFT atau REVISION")


def validate_courses(db: Session, nim: str, courses: list[MataKuliah]):
    result = build_validation_chain().validate(db, nim, courses)
    if not result.passed:
        raise HTTPException(400, result.message)


def add_course(db: Session, nim: str, semester: str, kode_mk: str) -> KRS:
    krs = get_or_create_krs(db, nim, semester); ensure_editable(krs)
    course = db.scalar(select(MataKuliah).options(selectinload(MataKuliah.schedules)).where(MataKuliah.kode_mk == kode_mk))
    if not course:
        raise HTTPException(404, "Mata kuliah tidak ditemukan")
    if any(detail.mata_kuliah_id == course.id for detail in krs.details):
        raise HTTPException(400, "Mata kuliah sudah ada dalam KRS")
    courses = [detail.mata_kuliah for detail in krs.details] + [course]
    validate_courses(db, nim, courses)
    db.add(KRSDetail(krs_id=krs.id, mata_kuliah_id=course.id)); db.commit()
    return load_krs(db, krs.id)


def remove_course(db: Session, nim: str, semester: str, kode_mk: str) -> KRS:
    krs = get_or_create_krs(db, nim, semester); ensure_editable(krs)
    detail = next((d for d in krs.details if d.mata_kuliah.kode_mk == kode_mk), None)
    if not detail:
        raise HTTPException(404, "Mata kuliah tidak ada dalam KRS")
    db.delete(detail); db.commit()
    return load_krs(db, krs.id)


def submit_krs(db: Session, nim: str, semester: str) -> KRS:
    krs = get_or_create_krs(db, nim, semester); ensure_editable(krs)
    if not krs.details:
        raise HTTPException(400, "KRS belum memiliki mata kuliah")
    validate_courses(db, nim, [detail.mata_kuliah for detail in krs.details])
    krs.status = KRSStatus.SUBMITTED; db.commit()
    return load_krs(db, krs.id)


def approve_krs(db: Session, nim: str, semester: str, dosen_pa_id: str) -> KRS:
    krs = get_or_create_krs(db, nim, semester)
    if krs.status != KRSStatus.SUBMITTED:
        raise HTTPException(400, "Hanya KRS berstatus SUBMITTED yang dapat disetujui")
    krs.status = KRSStatus.APPROVED; krs.dosen_pa_id = dosen_pa_id; db.commit()
    return load_krs(db, krs.id)


def request_revision(db: Session, nim: str, semester: str) -> KRS:
    krs = get_or_create_krs(db, nim, semester)
    if krs.status != KRSStatus.SUBMITTED:
        raise HTTPException(400, "Hanya KRS berstatus SUBMITTED yang dapat direvisi")
    krs.status = KRSStatus.REVISION; db.commit()
    return load_krs(db, krs.id)

