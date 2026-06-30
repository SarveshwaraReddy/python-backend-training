from api.repositories.payroll import PayrollRepository

class PayrollService:
    def __init__(self):
        self.repository = PayrollRepository()

    def get_all_payrolls(self):
        return self.repository.get_all_optimized()

    def get_payroll_by_id(self, pk):
        return self.repository.get_by_id(pk)

    def create_payroll(self, data):
        return self.repository.create(**data)

    def update_payroll(self, pk, data):
        payroll = self.repository.get_by_id(pk)
        if not payroll:
            return None
        return self.repository.update(payroll, **data)

    def delete_payroll(self, pk):
        payroll = self.repository.get_by_id(pk)
        if not payroll:
            return False
        self.repository.delete(payroll)
        return True
