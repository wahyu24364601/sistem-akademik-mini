from pydantic import BaseModel, Field


class GradeRequest(BaseModel):
    nim: str
    kode_mk: str
    semester: str
    nilai_huruf: str
    attendance_percent: float = Field(ge=0, le=100)
    changed_by: str = "DOSEN"
    reason: str = "Input nilai"


class GradeResponse(BaseModel):
    id: int
    nim: str
    kode_mk: str
    semester: str
    nilai_huruf: str
    nilai_angka: float
    attendance_percent: float


class GPAResponse(BaseModel):
    nim: str
    semester: str | None = None
    ips: float | None = None
    ipk: float | None = None
    total_sks: int
