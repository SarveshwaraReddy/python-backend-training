from api.repositories.base import BaseRepository
from accounts.models import User

class UserRepository(BaseRepository):
    model = User

    def get_by_email(self, email):
        try:
            return self.model.objects.get(email=email)
        except self.model.DoesNotExist:
            return None

    def get_by_employee_id(self, employee_id):
        try:
            return self.model.objects.get(employee_id=employee_id)
        except self.model.DoesNotExist:
            return None
