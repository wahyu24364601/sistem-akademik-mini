from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from .models import JalurMasuk, StatusPendaftaran


class RegisterRequest(BaseModel):
    nama_lengkap: str = Field(min_length=3, max_length=150)
    email: EmailStr
    phone: str
    tanggal_lahir: date
    alamat: str = Field(min_length=5, max_length=255)
    program_studi_id: int
    jalur_masuk: JalurMasuk

    @field_validator("phone")
    @classmethod
    def validate_indonesian_phone(cls, value: str) -> str:
        normalized = value.replace(" ", "").replace("-", "")
        if normalized.startswith("+62"):
            normalized = "0" + normalized[3:]
        if not normalized.startswith("08") or not normalized[2:].isdigit() or not 10 <= len(normalized) <= 14:
            raise ValueError("Nomor telepon harus nomor Indonesia valid, contoh: 081234567890")
        return normalized


class ApplicantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nama_lengkap: str
    email: EmailStr
    phone: str
    program_studi_id: int
    jalur_masuk: JalurMasuk
    status: StatusPendaftaran
    nim: str | None
    created_at: datetime
    approved_at: datetime | None


class ApprovalResponse(BaseModel):
    message: str
    applicant: ApplicantResponse


class StatsResponse(BaseModel):
    total: int
    pending: int
    approved: int
    rejected: int

