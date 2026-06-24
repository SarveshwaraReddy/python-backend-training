from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Department
from accounts.decorators import role_required


@role_required(['ADMIN', 'HR', 'MANAGER'])
def department_list(request):
    search = request.GET.get('search', '')
    departments = Department.objects.all()

    if search:
        departments = departments.filter(name__icontains=search)

    return render(request, 'departments/department_list.html', {
        'departments': departments,
        'search': search,
    })


@role_required(['ADMIN', 'HR'])
def department_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        Department.objects.create(name=name, description=description)
        messages.success(request, 'Department added successfully!')
        return redirect('departments:department_list')

    return render(request, 'departments/department_form.html', {
        'form_title': 'Add Department',
    })


@role_required(['ADMIN', 'HR'])
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)

    if request.method == 'POST':
        department.name = request.POST.get('name')
        department.description = request.POST.get('description')
        department.save()
        messages.success(request, 'Department updated successfully!')
        return redirect('departments:department_list')

    return render(request, 'departments/department_form.html', {
        'department': department,
        'form_title': 'Update Department',
    })


@role_required(['ADMIN', 'HR'])
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)

    if request.method == 'POST':
        department.delete()
        messages.success(request, 'Department deleted successfully!')
        return redirect('departments:department_list')

    return render(request, 'departments/department_confirm_delete.html', {
        'department': department,
    })
