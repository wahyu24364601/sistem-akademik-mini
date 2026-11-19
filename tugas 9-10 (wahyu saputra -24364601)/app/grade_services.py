from collections import defaultdict
from io import BytesIO

from fastapi import HTTPException
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .krs_models import Grade, GradeHistory, MataKuliah
from .models import CalonMahasiswa

GRADE_POINTS = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 2.0, "E": 0.0}


def grade_point(letter: str) -> float:
    point = GRADE_POINTS.get(letter.strip().upper())
    if point is None:
        raise HTTPException(400, "Nilai huruf harus A, B, C, D, atau E")
    return point


def serialise(grade: Grade):
    return {"id": grade.id, "nim": grade.nim, "kode_mk": grade.mata_kuliah.kode_mk,
            "semester": grade.semester, "nilai_huruf": grade.nilai_huruf,
            "nilai_angka": grade.nilai_angka, "attendance_percent": grade.attendance_percent}


def input_grade(db: Session, data):
    if data.attendance_percent < 75:
        raise HTTPException(400, "Nilai tidak dapat diinput karena presensi kurang dari 75%")
    course = db.scalar(select(MataKuliah).where(MataKuliah.kode_mk == data.kode_mk))
    if not course:
        raise HTTPException(404, "Mata kuliah tidak ditemukan")
    point, letter = grade_point(data.nilai_huruf), data.nilai_huruf.upper()
    grade = db.scalar(select(Grade).where(Grade.nim == data.nim, Grade.mata_kuliah_id == course.id, Grade.semester == data.semester))
    if grade:
        old = grade.nilai_huruf
        grade.nilai_huruf, grade.nilai_angka, grade.attendance_percent, grade.input_by = letter, point, data.attendance_percent, data.changed_by
        db.add(GradeHistory(grade=grade, old_value=old, new_value=letter, changed_by=data.changed_by, reason=data.reason))
    else:
        grade = Grade(nim=data.nim, mata_kuliah_id=course.id, semester=data.semester, nilai_huruf=letter,
                      nilai_angka=point, attendance_percent=data.attendance_percent, input_by=data.changed_by)
        db.add(grade)
    db.commit()
    return db.scalar(select(Grade).options(selectinload(Grade.mata_kuliah)).where(Grade.id == grade.id))


def all_grades(db: Session, nim: str):
    return db.scalars(select(Grade).options(selectinload(Grade.mata_kuliah)).where(Grade.nim == nim).order_by(Grade.semester, Grade.id)).all()


def effective_grades(grades):
    best = {}
    for grade in grades:
        if grade.nilai_angka >= 2.0 and (grade.mata_kuliah_id not in best or grade.nilai_angka > best[grade.mata_kuliah_id].nilai_angka):
            best[grade.mata_kuliah_id] = grade
    return list(best.values())


def calculate_gpa(grades):
    selected = effective_grades(grades)
    total_sks = sum(g.mata_kuliah.sks for g in selected)
    return (round(sum(g.mata_kuliah.sks * g.nilai_angka for g in selected) / total_sks, 2) if total_sks else 0.0, total_sks)


def calculate_ips(db: Session, nim: str, semester: str):
    return calculate_gpa([g for g in all_grades(db, nim) if g.semester == semester])


def calculate_ipk(db: Session, nim: str):
    return calculate_gpa(all_grades(db, nim))


def predicate(ipk: float) -> str:
    if ipk >= 3.5:
        return "Cum Laude"
    if ipk >= 3.0:
        return "Sangat Memuaskan"
    if ipk >= 2.5:
        return "Memuaskan"
    return "Cukup"


def transcript(db: Session, nim: str):
    grades = all_grades(db, nim)
    ipk, total_sks = calculate_gpa(grades)
    student = db.scalar(select(CalonMahasiswa).where(CalonMahasiswa.nim == nim))
    semesters = defaultdict(list)
    for item in grades:
        semesters[item.semester].append(serialise(item) | {"nama_mk": item.mata_kuliah.nama_mk, "sks": item.mata_kuliah.sks, "mutu": round(item.mata_kuliah.sks * item.nilai_angka, 2)})
    return {"nim": nim, "nama": student.nama_lengkap if student else "Mahasiswa", "program_studi": student.program_studi.nama if student and student.program_studi else "-",
            "semesters": dict(semesters), "total_sks": total_sks, "ipk": ipk, "predikat": predicate(ipk)}


def transcript_pdf(data: dict) -> bytes:
    stream = BytesIO()
    doc = SimpleDocTemplate(stream, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    style = getSampleStyleSheet()
    story = [Paragraph("INSTITUT SAINS DAN TEKNOLOGI NASIONAL (ISTN)", style["Title"]),
             Paragraph("TRANSKRIP AKADEMIK", style["Heading2"]), Spacer(1, 10),
             Paragraph(f"NIM: {data['nim']} &nbsp;&nbsp;&nbsp; Nama: {data['nama']}<br/>Program Studi: {data['program_studi']}", style["BodyText"]), Spacer(1, 10)]
    for semester, records in data["semesters"].items():
        story.append(Paragraph(f"Semester {semester}", style["Heading3"]))
        rows = [["Kode MK", "Mata Kuliah", "SKS", "Nilai", "Mutu"]] + [[r["kode_mk"], r["nama_mk"], str(r["sks"]), r["nilai_huruf"], f"{r['mutu']:.1f}"] for r in records]
        table = Table(rows, colWidths=[2.2*cm, 7.3*cm, 1.2*cm, 1.5*cm, 1.7*cm])
        table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#17365D")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), .4, colors.grey), ("ALIGN", (2,1), (-1,-1), "CENTER"), ("VALIGN", (0,0), (-1,-1), "MIDDLE")]))
        story += [table, Spacer(1, 8)]
    story += [Spacer(1, 8), Paragraph(f"Total SKS Lulus: {data['total_sks']}<br/>IPK: {data['ipk']:.2f}<br/>Predikat: {data['predikat']}", style["Heading3"]), Spacer(1, 25), Paragraph("Mengetahui,<br/>Dekan Fakultas", style["BodyText"])]
    doc.build(story)
    return stream.getvalue()
