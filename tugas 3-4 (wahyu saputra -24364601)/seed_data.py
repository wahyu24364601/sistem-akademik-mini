from app.database import Base, SessionLocal, engine
from app.models import ProgramStudi

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    if not db.query(ProgramStudi).filter_by(kode="INF").first():
        db.add(ProgramStudi(kode="INF", nama="Teknik Informatika", fakultas="Fakultas Teknologi Industri"))
        db.commit()
        print("Program Studi Teknik Informatika berhasil ditambahkan.")
    else:
        print("Data program studi sudah tersedia.")
finally:
    db.close()

