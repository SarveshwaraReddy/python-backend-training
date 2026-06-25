from api.repositories.base import BaseRepository
from departments.models import Department

class DepartmentRepository(BaseRepository):
    model = Department

    def get_all(self):
        return self.get_all_optimized()

    def get_all_optimized(self):
        # Module 11: optimize query count by prefetching related employees
        return self.model.objects.prefetch_related('employee_set').all()

    def get_by_id_optimized(self, pk):
        try:
            return self.model.objects.prefetch_related('employee_set').get(pk=pk)
        except self.model.DoesNotExist:
            return None
