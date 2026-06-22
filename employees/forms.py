from django import forms
from .models import Employee
import re
from datetime import date

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        widgets = {
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
            'profile_image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if not re.match(r'^EMP\d+$', employee_id):
            raise forms.ValidationError("Employee ID must start with 'EMP' followed by numbers (e.g., EMP001).")
        return employee_id

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match(r'^\d{10}$', phone):
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone

    def clean_salary(self):
        salary = self.cleaned_data.get('salary')
        if salary < 10000 or salary > 500000:
            raise forms.ValidationError("Salary must be between 10,000 and 500,000.")
        return salary

    def clean_joining_date(self):
        joining_date = self.cleaned_data.get('joining_date')
        if joining_date > date.today():
            raise forms.ValidationError("Joining date cannot be in the future.")
        return joining_date
