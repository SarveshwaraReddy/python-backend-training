from api.repositories.department import DepartmentRepository

class DepartmentService:
    def __init__(self):
        self.repository = DepartmentRepository()

    def get_all_departments(self):
        return self.repository.get_all()

    def get_department_by_id(self, pk):
        return self.repository.get_by_id(pk)

    def get_department_with_employees(self, pk):
        return self.repository.get_by_id_optimized(pk)

    def create_department(self, data):
        return self.repository.create(**data)

    def update_department(self, pk, data):
        dept = self.repository.get_by_id(pk)
        if not dept:
            return None
        return self.repository.update(dept, **data)

    def delete_department(self, pk):
        dept = self.repository.get_by_id(pk)
        if not dept:
            return False
        self.repository.delete(dept)
        return True
