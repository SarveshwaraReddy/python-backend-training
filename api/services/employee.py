from api.repositories.employee import EmployeeRepository

class EmployeeService:
    def __init__(self):
        self.repository = EmployeeRepository()

    def get_all_employees(self):
        return self.repository.get_all()

    def get_employee_by_id(self, pk):
        return self.repository.get_by_id(pk)

    def create_employee(self, data):
        if 'salary' not in data:
            data['salary'] = 10000.0
        if 'joining_date' not in data:
            import datetime
            data['joining_date'] = datetime.date.today()
        return self.repository.create(**data)
        

    def update_employee(self, pk, data):
        employee = self.repository.get_by_id(pk)
        if not employee:
            return None
        return self.repository.update(employee, **data)

    def delete_employee(self, pk):
        employee = self.repository.get_by_id(pk)
        if not employee:
            return False
        self.repository.delete(employee)
        return True
