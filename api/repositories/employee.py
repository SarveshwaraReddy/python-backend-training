from api.repositories.base import BaseRepository
from employees.models import Employee

class EmployeeRepository(BaseRepository):
    model = Employee

    def get_all(self):
        # Override to default to optimized query with select_related
        return self.get_all_optimized()

    def get_all_optimized(self):
        # Module 11: optimize query count by pre-joining department
        return self.model.objects.select_related('department').all()

    def get_by_employee_id(self, employee_id):
        try:
            return self.model.objects.select_related('department').get(employee_id=employee_id)
        except self.model.DoesNotExist:
            return None
