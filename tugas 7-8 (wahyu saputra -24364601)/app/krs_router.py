from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .krs_schemas import CourseRequest, CourseResponse, KRSResponse
from .krs_services import add_course, approve_krs, get_or_create_krs, remove_course, request_revision, submit_krs

router = APIRouter(prefix="/api/krs", tags=["KRS"])


def response(krs):
    return KRSResponse(
        nim=krs.nim, semester=krs.semester, status=krs.status, dosen_pa_id=krs.dosen_pa_id,
        total_sks=sum(detail.mata_kuliah.sks for detail in krs.details),
        courses=[CourseResponse(kode_mk=d.mata_kuliah.kode_mk, nama_mk=d.mata_kuliah.nama_mk, sks=d.mata_kuliah.sks) for d in krs.details],
    )


@router.get("/{nim}/{semester}", response_model=KRSResponse)
def get_krs(nim: str, semester: str, db: Session = Depends(get_db)):
    return response(get_or_create_krs(db, nim, semester))


@router.post("/{nim}/{semester}/courses", response_model=KRSResponse)
def add(nim: str, semester: str, payload: CourseRequest, db: Session = Depends(get_db)):
    return response(add_course(db, nim, semester, payload.kode_mk))


@router.delete("/{nim}/{semester}/courses/{kode_mk}", response_model=KRSResponse)
def remove(nim: str, semester: str, kode_mk: str, db: Session = Depends(get_db)):
    return response(remove_course(db, nim, semester, kode_mk))


@router.post("/{nim}/{semester}/submit", response_model=KRSResponse)
def submit(nim: str, semester: str, db: Session = Depends(get_db)):
    return response(submit_krs(db, nim, semester))


@router.put("/{nim}/{semester}/approve/{dosen_pa_id}", response_model=KRSResponse)
def approve(nim: str, semester: str, dosen_pa_id: str, db: Session = Depends(get_db)):
    return response(approve_krs(db, nim, semester, dosen_pa_id))


@router.put("/{nim}/{semester}/revision", response_model=KRSResponse)
def revision(nim: str, semester: str, db: Session = Depends(get_db)):
    return response(request_revision(db, nim, semester))

