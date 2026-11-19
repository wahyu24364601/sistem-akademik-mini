from datetime import time
from pydantic import BaseModel, Field


class ScheduleRequest(BaseModel):
    kode_mk: str
    hari: str
    jam_mulai: time
    jam_selesai: time
    kode_ruang: str
    dosen_id: str
    jumlah_mahasiswa: int = Field(ge=1)


class ScheduleResponse(BaseModel):
    id: int
    kode_mk: str
    hari: str
    jam_mulai: time
    jam_selesai: time
    kode_ruang: str
    dosen_id: str | None
    jumlah_mahasiswa: int

