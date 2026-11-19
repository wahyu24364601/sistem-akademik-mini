from dataclasses import dataclass
from datetime import time
from sqlalchemy import select
from sqlalchemy.orm import Session
from .krs_models import AcademicRecord, MataKuliah, Prerequisite


GRADE_POINTS = {"A": 4, "B": 3, "C": 2, "D": 1, "E": 0}


@dataclass
class ValidationResult:
    passed: bool
    message: str = ""


class Validator:
    def __init__(self, next_validator=None):
        self.next_validator = next_validator

    def validate(self, db: Session, nim: str, courses: list[MataKuliah]) -> ValidationResult:
        result = self.check(db, nim, courses)
        if not result.passed or self.next_validator is None:
            return result
        return self.next_validator.validate(db, nim, courses)

    def check(self, db, nim, courses) -> ValidationResult:
        raise NotImplementedError


class SKSValidator(Validator):
    def check(self, db, nim, courses):
        total = sum(course.sks for course in courses)
        if total > 24:
            return ValidationResult(False, f"Total SKS {total} melebihi batas maksimal 24 SKS")
        return ValidationResult(True)


class DuplicateValidator(Validator):
    def check(self, db, nim, courses):
        ids = [course.id for course in courses]
        if len(ids) != len(set(ids)):
            return ValidationResult(False, "Mata kuliah tidak boleh dipilih dua kali")
        return ValidationResult(True)


class PrerequisiteValidator(Validator):
    def check(self, db, nim, courses):
        for course in courses:
            prerequisites = db.scalars(select(Prerequisite).where(Prerequisite.mata_kuliah_id == course.id)).all()
            for prerequisite in prerequisites:
                record = db.scalar(select(AcademicRecord).where(
                    AcademicRecord.nim == nim,
                    AcademicRecord.mata_kuliah_id == prerequisite.prerequisite_id,
                ))
                if not record or GRADE_POINTS.get(record.nilai_huruf, 0) < 2:
                    return ValidationResult(False, f"Prasyarat belum terpenuhi untuk {course.kode_mk}")
        return ValidationResult(True)


class ConflictValidator(Validator):
    def check(self, db, nim, courses):
        schedules = []
        for course in courses:
            for schedule in course.schedules:
                schedules.append((course.kode_mk, schedule.hari, schedule.jam_mulai, schedule.jam_selesai))
        for index, first in enumerate(schedules):
            for second in schedules[index + 1:]:
                if first[1] == second[1] and first[2] < second[3] and second[2] < first[3]:
                    return ValidationResult(False, f"Jadwal bentrok antara {first[0]} dan {second[0]}")
        return ValidationResult(True)


def build_validation_chain() -> Validator:
    return DuplicateValidator(PrerequisiteValidator(SKSValidator(ConflictValidator())))

