from api.repositories.attendance import AttendanceRepository

class AttendanceService:
    def __init__(self):
        self.repository = AttendanceRepository()

    def get_all_attendances(self):
        return self.repository.get_all_optimized()

    def get_attendance_by_id(self, pk):
        return self.repository.get_by_id(pk)

    def create_attendance(self, data):
        return self.repository.create(**data)

    def update_attendance(self, pk, data):
        attendance = self.repository.get_by_id(pk)
        if not attendance:
            return None
        return self.repository.update(attendance, **data)

    def delete_attendance(self, pk):
        attendance = self.repository.get_by_id(pk)
        if not attendance:
            return False
        self.repository.delete(attendance)
        return True
