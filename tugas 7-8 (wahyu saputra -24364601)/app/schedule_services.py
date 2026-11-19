from datetime import time
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from .krs_models import JadwalKuliah, KRS, KRSDetail, KRSStatus, MataKuliah, Ruangan
from .schedule_observer import notification_manager


def serialise(schedule: JadwalKuliah):
    return {"id": schedule.id, "kode_mk": schedule.mata_kuliah.kode_mk, "hari": schedule.hari,
            "jam_mulai": schedule.jam_mulai, "jam_selesai": schedule.jam_selesai,
            "kode_ruang": schedule.ruangan.kode_ruang, "dosen_id": schedule.dosen_id,
            "jumlah_mahasiswa": schedule.jumlah_mahasiswa}


def load_schedule(db: Session, schedule_id: int):
    item = db.scalar(select(JadwalKuliah).options(selectinload(JadwalKuliah.mata_kuliah), selectinload(JadwalKuliah.ruangan)).where(JadwalKuliah.id == schedule_id))
    if not item:
        raise HTTPException(404, "Jadwal tidak ditemukan")
    return item


def conflicts_for(db: Session, target: JadwalKuliah, exclude_id: int | None = None):
    schedules = db.scalars(select(JadwalKuliah).options(selectinload(JadwalKuliah.mata_kuliah), selectinload(JadwalKuliah.ruangan)).where(JadwalKuliah.hari == target.hari)).all()
    conflicts = []
    for other in schedules:
        if other.id == exclude_id or other.id == target.id:
            continue
        overlap = target.jam_mulai < other.jam_selesai and other.jam_mulai < target.jam_selesai
        if not overlap:
            continue
        if target.ruangan_id == other.ruangan_id:
            conflicts.append({"type": "room_conflict", "schedules": [target.id, other.id]})
        if target.dosen_id and target.dosen_id == other.dosen_id:
            conflicts.append({"type": "lecturer_conflict", "schedules": [target.id, other.id]})
        if target.ruangan_id == other.ruangan_id or (target.dosen_id and target.dosen_id == other.dosen_id):
            conflicts.append({"type": "time_overlap", "schedules": [target.id, other.id]})
    return conflicts


def validate_schedule(db: Session, schedule: JadwalKuliah, exclude_id=None):
    if schedule.jam_mulai >= schedule.jam_selesai:
        raise HTTPException(400, "Jam mulai harus lebih awal dari jam selesai")
    if schedule.jumlah_mahasiswa > schedule.ruangan.kapasitas:
        raise HTTPException(400, "Kapasitas ruangan tidak mencukupi")
    conflicts = conflicts_for(db, schedule, exclude_id)
    if conflicts:
        raise HTTPException(400, {"message": "Jadwal bentrok", "conflicts": conflicts})


def create_schedule(db: Session, data):
    course = db.scalar(select(MataKuliah).where(MataKuliah.kode_mk == data.kode_mk))
    room = db.scalar(select(Ruangan).where(Ruangan.kode_ruang == data.kode_ruang))
    if not course or not room:
        raise HTTPException(404, "Mata kuliah atau ruangan tidak ditemukan")
    schedule = JadwalKuliah(mata_kuliah_id=course.id, hari=data.hari, jam_mulai=data.jam_mulai, jam_selesai=data.jam_selesai,
                            ruangan_id=room.id, dosen_id=data.dosen_id, jumlah_mahasiswa=data.jumlah_mahasiswa)
    db.add(schedule); db.flush(); schedule.ruangan = room
    validate_schedule(db, schedule); db.commit()
    schedule = load_schedule(db, schedule.id)
    notification_manager.notify("SCHEDULE_CREATED", serialise(schedule))
    return schedule


def update_schedule(db: Session, schedule_id: int, data):
    schedule = load_schedule(db, schedule_id)
    course = db.scalar(select(MataKuliah).where(MataKuliah.kode_mk == data.kode_mk))
    room = db.scalar(select(Ruangan).where(Ruangan.kode_ruang == data.kode_ruang))
    if not course or not room:
        raise HTTPException(404, "Mata kuliah atau ruangan tidak ditemukan")
    schedule.mata_kuliah_id, schedule.hari, schedule.jam_mulai, schedule.jam_selesai = course.id, data.hari, data.jam_mulai, data.jam_selesai
    schedule.ruangan_id, schedule.dosen_id, schedule.jumlah_mahasiswa, schedule.ruangan = room.id, data.dosen_id, data.jumlah_mahasiswa, room
    validate_schedule(db, schedule, exclude_id=schedule.id)
    # Jadwal berubah: KRS terdampak kembali ke REVISION untuk ditinjau.
    affected = db.scalars(select(KRS).join(KRSDetail).where(KRSDetail.mata_kuliah_id == course.id, KRS.status.in_([KRSStatus.SUBMITTED, KRSStatus.APPROVED]))).all()
    for krs in affected:
        krs.status = KRSStatus.REVISION
    db.commit(); schedule = load_schedule(db, schedule.id)
    notification_manager.notify("SCHEDULE_CHANGED", serialise(schedule))
    return schedule


def suggest_alternatives(db: Session, schedule_id: int):
    schedule = load_schedule(db, schedule_id)
    suggestions = []
    for day in ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]:
        for start, end in [(time(8), time(10)), (time(10), time(12)), (time(13), time(15))]:
            candidate = JadwalKuliah(id=-1, mata_kuliah_id=schedule.mata_kuliah_id, hari=day, jam_mulai=start, jam_selesai=end,
                                     ruangan_id=schedule.ruangan_id, dosen_id=schedule.dosen_id, jumlah_mahasiswa=schedule.jumlah_mahasiswa)
            candidate.ruangan = schedule.ruangan
            if not conflicts_for(db, candidate) and schedule.jumlah_mahasiswa <= schedule.ruangan.kapasitas:
                suggestions.append({"hari": day, "jam": f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}", "ruangan": schedule.ruangan.kode_ruang, "reason": "Tidak bentrok, kapasitas mencukupi"})
            if len(suggestions) == 3:
                return suggestions
    return suggestions
