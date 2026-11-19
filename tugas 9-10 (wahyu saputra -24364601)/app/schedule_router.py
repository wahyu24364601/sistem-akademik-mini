from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from .database import get_db
from .krs_models import JadwalKuliah
from .schedule_schemas import ScheduleRequest, ScheduleResponse
from .schedule_services import create_schedule, load_schedule, serialise, suggest_alternatives, update_schedule

router = APIRouter(prefix="/api/schedules", tags=["Jadwal & Ruangan"])

@router.post("", response_model=ScheduleResponse)
def create(payload: ScheduleRequest, db: Session = Depends(get_db)):
    return serialise(create_schedule(db, payload))

@router.put("/{schedule_id}", response_model=ScheduleResponse)
def update(schedule_id: int, payload: ScheduleRequest, db: Session = Depends(get_db)):
    return serialise(update_schedule(db, schedule_id, payload))

@router.get("/conflicts")
def all_conflicts(db: Session = Depends(get_db)):
    from .schedule_services import conflicts_for
    schedules = db.scalars(select(JadwalKuliah).options(selectinload(JadwalKuliah.mata_kuliah), selectinload(JadwalKuliah.ruangan))).all()
    result, seen = [], set()
    for item in schedules:
        for conflict in conflicts_for(db, item):
            key = (conflict["type"], tuple(sorted(conflict["schedules"])))
            if key not in seen:
                result.append(conflict); seen.add(key)
    return {"conflicts": result}

@router.get("/{schedule_id}/alternatives")
def alternatives(schedule_id: int, db: Session = Depends(get_db)):
    return {"alternatives": suggest_alternatives(db, schedule_id)}

@router.delete("/{schedule_id}")
def delete(schedule_id: int, db: Session = Depends(get_db)):
    schedule = load_schedule(db, schedule_id)
    db.delete(schedule); db.commit()
    return {"message": "Jadwal dihapus"}

