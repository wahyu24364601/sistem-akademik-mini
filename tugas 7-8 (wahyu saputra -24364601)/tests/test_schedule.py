from datetime import time

from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.krs_models import JadwalKuliah, MataKuliah, Ruangan
from app.main import app

client = TestClient(app)


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    courses = [
        MataKuliah(kode_mk="JDL101", nama_mk="Rekayasa Perangkat Lunak", sks=3),
        MataKuliah(kode_mk="JDL102", nama_mk="Jaringan Komputer", sks=3),
        MataKuliah(kode_mk="JDL103", nama_mk="Sistem Operasi", sks=3),
    ]
    rooms = [Ruangan(kode_ruang="A101", kapasitas=30), Ruangan(kode_ruang="B201", kapasitas=10)]
    db.add_all(courses + rooms)
    db.flush()
    db.add(JadwalKuliah(mata_kuliah_id=courses[0].id, hari="Senin", jam_mulai=time(8), jam_selesai=time(10),
                         ruangan_id=rooms[0].id, dosen_id="DSN001", jumlah_mahasiswa=25))
    db.commit()
    db.close()


def payload(kode_mk="JDL102", kode_ruang="A101", dosen_id="DSN002", jumlah_mahasiswa=20, jam_mulai="09:00:00", jam_selesai="11:00:00"):
    return {"kode_mk": kode_mk, "hari": "Senin", "jam_mulai": jam_mulai, "jam_selesai": jam_selesai,
            "kode_ruang": kode_ruang, "dosen_id": dosen_id, "jumlah_mahasiswa": jumlah_mahasiswa}


def test_room_conflict_rejected():
    response = client.post("/api/schedules", json=payload())
    assert response.status_code == 400
    assert "room_conflict" in str(response.json())


def test_lecturer_conflict_rejected():
    response = client.post("/api/schedules", json=payload(kode_ruang="B201", dosen_id="DSN001", jumlah_mahasiswa=8))
    assert response.status_code == 400
    assert "lecturer_conflict" in str(response.json())


def test_capacity_rejected():
    response = client.post("/api/schedules", json=payload(kode_ruang="B201", jumlah_mahasiswa=11, jam_mulai="13:00:00", jam_selesai="15:00:00"))
    assert response.status_code == 400
    assert "Kapasitas" in response.json()["detail"]


def test_create_update_and_alternatives():
    created = client.post("/api/schedules", json=payload(kode_ruang="B201", jumlah_mahasiswa=8, jam_mulai="13:00:00", jam_selesai="15:00:00"))
    assert created.status_code == 200
    schedule_id = created.json()["id"]
    alternatives = client.get(f"/api/schedules/{schedule_id}/alternatives")
    assert alternatives.status_code == 200
    assert alternatives.json()["alternatives"]
    changed = client.put(f"/api/schedules/{schedule_id}", json=payload(kode_ruang="B201", jumlah_mahasiswa=8, jam_mulai="10:00:00", jam_selesai="12:00:00"))
    assert changed.status_code == 200
