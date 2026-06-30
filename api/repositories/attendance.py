from api.repositories.base import BaseRepository
from attendance.models import Attendance

class AttendanceRepository(BaseRepository):
    model = Attendance

    def get_all_optimized(self):
        return self.model.objects.select_related('employee').all()
