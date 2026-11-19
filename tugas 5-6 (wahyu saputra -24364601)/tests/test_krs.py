from datetime import date, time
from types import SimpleNamespace
from hypothesis import given, strategies as st
from fastapi.testclient import TestClient
from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import CalonMahasiswa, JalurMasuk, ProgramStudi, StatusPendaftaran
from app.krs_models import AcademicRecord, JadwalKuliah, MataKuliah, Prerequisite
from app.krs_validators import SKSValidator

client = TestClient(app)


def setup_module():
    Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    prodi = ProgramStudi(kode="INF", nama="Teknik Informatika", fakultas="FTI")
    db.add(prodi); db.flush()
    courses = [
        MataKuliah(kode_mk="INF101", nama_mk="Algoritma", sks=3),
        MataKuliah(kode_mk="INF102", nama_mk="Basis Data", sks=3),
        MataKuliah(kode_mk="INF103", nama_mk="PBO", sks=3),
        MataKuliah(kode_mk="INF104", nama_mk="AI", sks=3),
        MataKuliah(kode_mk="INF105", nama_mk="Data Mining", sks=3),
    ]
    db.add_all(courses); db.flush()
    db.add_all([
        JadwalKuliah(mata_kuliah_id=courses[0].id, hari="Senin", jam_mulai=time(8), jam_selesai=time(10)),
        JadwalKuliah(mata_kuliah_id=courses[1].id, hari="Senin", jam_mulai=time(10), jam_selesai=time(12)),
        JadwalKuliah(mata_kuliah_id=courses[2].id, hari="Selasa", jam_mulai=time(8), jam_selesai=time(10)),
        JadwalKuliah(mata_kuliah_id=courses[3].id, hari="Senin", jam_mulai=time(9), jam_selesai=time(11)),
        Prerequisite(mata_kuliah_id=courses[4].id, prerequisite_id=courses[2].id),
    ])
    for number in range(2, 7):
        nim = f"2026INF-{number:04d}"
        db.add(CalonMahasiswa(nama_lengkap=f"Mahasiswa {number}", email=f"m{number}@test.id", phone="081234567890",
               tanggal_lahir=date(2005, 1, 1), alamat="Jakarta", program_studi_id=prodi.id,
               jalur_masuk=JalurMasuk.MANDIRI, status=StatusPendaftaran.APPROVED, nim=nim))
    db.commit(); db.close()


def test_add_course_success():
    response = client.post("/api/krs/2026INF-0002/2026-1/courses", json={"kode_mk": "INF101"})
    assert response.status_code == 200
    assert response.json()["total_sks"] == 3


def test_duplicate_course_rejected():
    response = client.post("/api/krs/2026INF-0002/2026-1/courses", json={"kode_mk": "INF101"})
    assert response.status_code == 400


def test_prerequisite_rejected():
    response = client.post("/api/krs/2026INF-0003/2026-1/courses", json={"kode_mk": "INF105"})
    assert response.status_code == 400
    assert "Prasyarat" in response.json()["detail"]


def test_schedule_conflict_rejected():
    client.post("/api/krs/2026INF-0004/2026-1/courses", json={"kode_mk": "INF101"})
    response = client.post("/api/krs/2026INF-0004/2026-1/courses", json={"kode_mk": "INF104"})
    assert response.status_code == 400
    assert "bentrok" in response.json()["detail"].lower()


def test_submit_then_approve_krs():
    client.post("/api/krs/2026INF-0005/2026-1/courses", json={"kode_mk": "INF101"})
    submitted = client.post("/api/krs/2026INF-0005/2026-1/submit")
    assert submitted.json()["status"] == "SUBMITTED"
    approved = client.put("/api/krs/2026INF-0005/2026-1/approve/DPA001")
    assert approved.json()["status"] == "APPROVED"
    assert approved.json()["dosen_pa_id"] == "DPA001"


@given(st.lists(st.integers(min_value=1, max_value=4), min_size=1, max_size=30))
def test_total_sks_never_passes_above_24(sks_list):
    courses = [SimpleNamespace(sks=sks) for sks in sks_list]
    result = SKSValidator().check(None, "NIM", courses)
    assert result.passed == (sum(sks_list) <= 24)

