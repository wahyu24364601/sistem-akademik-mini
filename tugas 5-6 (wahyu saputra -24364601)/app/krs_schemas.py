from pydantic import BaseModel, ConfigDict
from .krs_models import KRSStatus


class CourseRequest(BaseModel):
    kode_mk: str


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    kode_mk: str
    nama_mk: str
    sks: int


class KRSResponse(BaseModel):
    nim: str
    semester: str
    status: KRSStatus
    total_sks: int
    courses: list[CourseResponse]
    dosen_pa_id: str | None

