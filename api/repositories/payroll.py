from api.repositories.base import BaseRepository
from payroll.models import Payroll

class PayrollRepository(BaseRepository):
    model = Payroll

    def get_all_optimized(self):
        return self.model.objects.select_related('employee').all()
