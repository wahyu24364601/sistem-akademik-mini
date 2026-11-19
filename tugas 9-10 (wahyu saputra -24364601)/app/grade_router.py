from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .grade_schemas import GPAResponse, GradeRequest, GradeResponse
from .grade_services import all_grades, calculate_ipk, calculate_ips, input_grade, serialise, transcript, transcript_pdf
from .krs_models import Grade, GradeHistory

router = APIRouter(prefix="/api/grades", tags=["Nilai & Transkrip"])

@router.post("", response_model=GradeResponse)
def create_or_update(payload: GradeRequest, db: Session = Depends(get_db)):
    return serialise(input_grade(db, payload))

@router.get("/{nim}/ips/{semester}", response_model=GPAResponse)
def ips(nim: str, semester: str, db: Session = Depends(get_db)):
    value, sks = calculate_ips(db, nim, semester)
    return {"nim": nim, "semester": semester, "ips": value, "total_sks": sks}

@router.get("/{nim}/ipk", response_model=GPAResponse)
def ipk(nim: str, db: Session = Depends(get_db)):
    value, sks = calculate_ipk(db, nim)
    return {"nim": nim, "ipk": value, "total_sks": sks}

@router.get("/{nim}/transcript")
def get_transcript(nim: str, db: Session = Depends(get_db)):
    return transcript(db, nim)

@router.get("/{nim}/transcript.pdf")
def get_transcript_pdf(nim: str, db: Session = Depends(get_db)):
    content = transcript_pdf(transcript(db, nim))
    return Response(content=content, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="transkrip_{nim}.pdf"'})

@router.get("/{nim}/history")
def history(nim: str, db: Session = Depends(get_db)):
    rows = db.execute(select(GradeHistory, Grade).join(Grade).where(Grade.nim == nim).order_by(GradeHistory.changed_at.desc())).all()
    return {"history": [{"grade_id": h.grade_id, "old_value": h.old_value, "new_value": h.new_value, "changed_by": h.changed_by, "reason": h.reason, "changed_at": h.changed_at} for h, _ in rows]}
