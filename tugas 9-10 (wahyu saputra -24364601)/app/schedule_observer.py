import logging

logger = logging.getLogger("schedule_notifications")


class ScheduleObserver:
    role = "stakeholder"
    def update(self, event_type: str, schedule_data: dict):
        logger.info("[%s] %s: %s", self.role, event_type, schedule_data)


class StudentObserver(ScheduleObserver):
    role = "Mahasiswa (simulasi Email/Push)"


class LecturerObserver(ScheduleObserver):
    role = "Dosen (simulasi Email/Push)"


class AcademicAdminObserver(ScheduleObserver):
    role = "Admin Akademik (simulasi Dashboard)"


class ScheduleSubject:
    def __init__(self):
        self.observers = [StudentObserver(), LecturerObserver(), AcademicAdminObserver()]

    def notify(self, event_type: str, schedule_data: dict):
        for observer in self.observers:
            observer.update(event_type, schedule_data)


notification_manager = ScheduleSubject()
