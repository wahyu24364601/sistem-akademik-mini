import os
os.environ["DATABASE_URL"] = "sqlite:///./test_sistem_akademik.db"

from fastapi.testclient import TestClient
from app.database import Base, engine, SessionLocal
from app.main import app
from app.models import ProgramStudi

client = TestClient(app)

def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.add(ProgramStudi(kode="INF", nama="Teknik Informatika", fakultas="FTI"))
    db.commit(); db.close()

def payload(email="siti@example.com", phone="081234567890"):
    return {"nama_lengkap":"Siti Aminah","email":email,"phone":phone,
            "tanggal_lahir":"2007-05-20","alamat":"Jakarta Selatan",
            "program_studi_id":1,"jalur_masuk":"Mandiri"}

def test_register_success():
    response = client.post("/api/pmb/register", json=payload())
    assert response.status_code == 201
    assert response.json()["status"] == "pending"

def test_duplicate_email_returns_409():
    response = client.post("/api/pmb/register", json=payload())
    assert response.status_code == 409

def test_invalid_phone_returns_422():
    response = client.post("/api/pmb/register", json=payload("baru@example.com", "123"))
    assert response.status_code == 422

def test_approve_generates_idempotent_nim():
    response = client.put("/api/pmb/approve/1")
    assert response.status_code == 200
    nim = response.json()["applicant"]["nim"]
    assert nim.endswith("INF-0001")
    again = client.put("/api/pmb/approve/1")
    assert again.json()["applicant"]["nim"] == nim

