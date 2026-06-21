from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from departments.models import Department
from .models import Employee


def home(request):
    return render(request, 'employees/home.html')


def about(request):
    return render(request, 'employees/about.html')


def contact(request):
    return render(request, 'employees/contact.html')


def employee_list(request):
    search = request.GET.get('search', '')
    department_id = request.GET.get('department', '')

    employees = Employee.objects.all()

    if search:
        employees = employees.filter(
            first_name__icontains=search
        ) | employees.filter(
            employee_id__icontains=search
        ) | employees.filter(
            email__icontains=search
        )

    if department_id:
        employees = employees.filter(department_id=department_id)

    departments = Department.objects.all()

    return render(request, 'employees/employee_list.html', {
        'employees': employees,
        'departments': departments,
        'search': search,
        'selected_department': department_id,
    })


def employee_add(request):
    departments = Department.objects.all()

    if request.method == 'POST':
        Employee.objects.create(
            employee_id=request.POST.get('employee_id'),
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            salary=request.POST.get('salary'),
            joining_date=request.POST.get('joining_date'),
            designation=request.POST.get('designation'),
            department_id=request.POST.get('department'),
            status=request.POST.get('status'),
        )
        messages.success(request, 'Employee added successfully!')
        return redirect('employees:employee_list')

    return render(request, 'employees/employee_form.html', {
        'departments': departments,
        'form_title': 'Add Employee',
    })


def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    departments = Department.objects.all()

    if request.method == 'POST':
        employee.employee_id = request.POST.get('employee_id')
        employee.first_name = request.POST.get('first_name')
        employee.last_name = request.POST.get('last_name')
        employee.email = request.POST.get('email')
        employee.phone = request.POST.get('phone')
        employee.salary = request.POST.get('salary')
        employee.joining_date = request.POST.get('joining_date')
        employee.designation = request.POST.get('designation')
        employee.department_id = request.POST.get('department')
        employee.status = request.POST.get('status')
        employee.save()
        messages.success(request, 'Employee updated successfully!')
        return redirect('employees:employee_list')

    return render(request, 'employees/employee_form.html', {
        'employee': employee,
        'departments': departments,
        'form_title': 'Update Employee',
    })


def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted successfully!')
        return redirect('employees:employee_list')

    return render(request, 'employees/employee_confirm_delete.html', {
        'employee': employee,
    })
