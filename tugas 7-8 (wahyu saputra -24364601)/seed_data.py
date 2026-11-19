from app.database import Base, SessionLocal, engine
from app.models import CalonMahasiswa, JalurMasuk, ProgramStudi, StatusPendaftaran
from app.krs_models import AcademicRecord, JadwalKuliah, MataKuliah, Prerequisite, Ruangan
from datetime import date, time

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    prodi = db.query(ProgramStudi).filter_by(kode="INF").first()
    if not prodi:
        prodi = ProgramStudi(kode="INF", nama="Teknik Informatika", fakultas="Fakultas Teknologi Industri")
        db.add(prodi); db.commit(); db.refresh(prodi)
    if not db.query(CalonMahasiswa).filter_by(nim="2026INF-0001").first():
        db.add(CalonMahasiswa(nama_lengkap="Mahasiswa Demo", email="demo@istn.ac.id", phone="081234567890",
               tanggal_lahir=date(2005, 1, 1), alamat="Jakarta", program_studi_id=prodi.id,
               jalur_masuk=JalurMasuk.MANDIRI, status=StatusPendaftaran.APPROVED, nim="2026INF-0001"))
    if not db.query(Ruangan).filter_by(kode_ruang="A101").first():
        db.add_all([Ruangan(kode_ruang="A101", kapasitas=40), Ruangan(kode_ruang="B201", kapasitas=30)])
        db.flush()
    a101 = db.query(Ruangan).filter_by(kode_ruang="A101").one()
    b201 = db.query(Ruangan).filter_by(kode_ruang="B201").one()
    if not db.query(MataKuliah).filter_by(kode_mk="INF101").first():
        algo = MataKuliah(kode_mk="INF101", nama_mk="Algoritma dan Pemrograman", sks=3)
        basis = MataKuliah(kode_mk="INF102", nama_mk="Basis Data", sks=3)
        pbo = MataKuliah(kode_mk="INF103", nama_mk="Pemrograman Berorientasi Objek", sks=3)
        conflict = MataKuliah(kode_mk="INF104", nama_mk="Kecerdasan Buatan", sks=3)
        db.add_all([algo, basis, pbo, conflict]); db.flush()
        db.add_all([
            JadwalKuliah(mata_kuliah_id=algo.id, hari="Senin", jam_mulai=time(8), jam_selesai=time(10), ruangan_id=a101.id, dosen_id="DSN001", jumlah_mahasiswa=35),
            JadwalKuliah(mata_kuliah_id=basis.id, hari="Senin", jam_mulai=time(10), jam_selesai=time(12), ruangan_id=a101.id, dosen_id="DSN002", jumlah_mahasiswa=35),
            JadwalKuliah(mata_kuliah_id=pbo.id, hari="Selasa", jam_mulai=time(8), jam_selesai=time(10), ruangan_id=b201.id, dosen_id="DSN003", jumlah_mahasiswa=25),
            JadwalKuliah(mata_kuliah_id=conflict.id, hari="Senin", jam_mulai=time(9), jam_selesai=time(11), ruangan_id=b201.id, dosen_id="DSN004", jumlah_mahasiswa=25),
            Prerequisite(mata_kuliah_id=basis.id, prerequisite_id=algo.id),
            AcademicRecord(nim="2026INF-0001", mata_kuliah_id=algo.id, nilai_huruf="B", semester="2025-2"),
        ])
    db.commit()
    print("Data PMB dan KRS demo siap digunakan.")
finally:
    db.close()

