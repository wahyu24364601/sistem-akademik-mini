from fastapi import Depends, FastAPI, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import CalonMahasiswa, StatusPendaftaran
from . import krs_models  # registers KRS tables in SQLAlchemy metadata
from .krs_router import router as krs_router
from .schemas import ApplicantResponse, ApprovalResponse, RegisterRequest, StatsResponse
from .services import approve_applicant, register_applicant

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Sistem Akademik Mini - PMB API", version="1.0.0")
app.include_router(krs_router)


@app.post("/api/pmb/register", response_model=ApplicantResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return register_applicant(db, payload)


@app.get("/api/pmb/status/{applicant_id}", response_model=ApplicantResponse)
def get_status(applicant_id: int, db: Session = Depends(get_db)):
    applicant = db.get(CalonMahasiswa, applicant_id)
    if not applicant:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Pendaftar tidak ditemukan")
    return applicant


@app.put("/api/pmb/approve/{applicant_id}", response_model=ApprovalResponse)
def approve(applicant_id: int, db: Session = Depends(get_db)):
    applicant = approve_applicant(db, applicant_id)
    return {"message": "Pendaftaran disetujui", "applicant": applicant}


@app.get("/api/pmb/stats", response_model=StatsResponse)
def stats(db: Session = Depends(get_db)):
    def count(state: StatusPendaftaran | None = None) -> int:
        query = select(func.count()).select_from(CalonMahasiswa)
        if state:
            query = query.where(CalonMahasiswa.status == state)
        return db.scalar(query) or 0
    return StatsResponse(
        total=count(), pending=count(StatusPendaftaran.PENDING),
        approved=count(StatusPendaftaran.APPROVED), rejected=count(StatusPendaftaran.REJECTED)
    )

