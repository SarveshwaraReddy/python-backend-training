from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count, Avg, Max, Min, Sum, F, FloatField
from django.db.models.functions import Coalesce
from api.responses.custom_response import SuccessResponse
from employees.models import Employee
from departments.models import Department
from payroll.models import Payroll
from attendance.models import Attendance
import datetime

class ORMReportsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, report_type=None):
        # Allow ADMIN and HR roles to view reports
        if request.user.role not in ['ADMIN', 'HR']:
            return Response({"success": False, "message": "Permission Denied"}, status=403)

        if report_type == 'top-salaries':
            # Module 1 & 10: Top 10 Highest Paid Employees using ORM
            data = Employee.objects.select_related('department').order_by('-salary')[:10].values(
                'employee_id', 'first_name', 'last_name', 'salary', 'designation'
            )
            return SuccessResponse(data=list(data), message="Top salary report generated successfully")

        elif report_type == 'department-summary':
            # Module 1, 5, 10: Department-wise Employee Count & Average Salary using ORM
            data = Department.objects.annotate(
                total_employees=Count('employee'),
                average_salary=Coalesce(Avg('employee__salary'), 0.0, output_field=FloatField())
            ).values('name', 'total_employees', 'average_salary')
            
            mapped_data = []
            for item in data:
                mapped_data.append({
                    'department_name': item['name'],
                    'total_employees': item['total_employees'],
                    'average_salary': float(item['average_salary'])
                })
            return SuccessResponse(data=mapped_data, message="Department summary report generated successfully")

        elif report_type == 'monthly-payroll':
            # Module 1 & 10: Monthly Salary Statistics using ORM
            data = Payroll.objects.values('month').annotate(
                employees_paid=Count('id'),
                total_paid=Coalesce(Sum('net_salary'), 0.0, output_field=FloatField())
            ).order_by('-month')

            
            mapped_data = []
            for item in data:
                mapped_data.append({
                    'month': item['month'],
                    'employees_paid': item['employees_paid'],
                    'total_paid': float(item['total_paid'])
                })
            return SuccessResponse(data=mapped_data, message="Monthly payroll report generated successfully")

        elif report_type == 'attendance-summary':
            # Module 1 & 10: Attendance summary using ORM
            data = Attendance.objects.select_related('employee').annotate(
                employee_id=F('employee__employee_id'),
                first_name=F('employee__first_name'),
                last_name=F('employee__last_name')
            ).values('employee_id', 'first_name', 'last_name', 'date', 'status').order_by('-date')
            return SuccessResponse(data=list(data), message="Attendance report generated successfully")

        elif report_type == 'joined-this-month':
            # Module 1: Employees Joined This Month
            today = datetime.date.today()
            data = Employee.objects.filter(
                joining_date__year=today.year, 
                joining_date__month=today.month
            ).values('employee_id', 'first_name', 'last_name', 'joining_date', 'designation')
            return SuccessResponse(data=list(data), message="Joined this month report generated successfully")

        else:
            return Response({
                "success": False,
                "message": "Invalid report type. Choose top-salaries, department-summary, monthly-payroll, attendance-summary, or joined-this-month."
            }, status=400)

    def post(self, request, report_type=None):
        """
        Triggers asynchronous PDF report generation for the given report type.
        """
        if request.user.role not in ['ADMIN', 'HR']:
            return Response({"success": False, "message": "Permission Denied"}, status=403)
            
        from company_portal.tasks.report_tasks import generate_attendance_report, generate_department_report
        
        if report_type == 'attendance-summary':
            month = request.data.get('month')
            task = getattr(generate_attendance_report, 'delay')(month)
            return SuccessResponse(
                data={"task_id": task.id},
                message="Attendance report generation queued successfully",
                status=202
            )
        elif report_type == 'department-summary':
            task = getattr(generate_department_report, 'delay')()
            return SuccessResponse(
                data={"task_id": task.id},
                message="Department summary report generation queued successfully",
                status=202
            )
        else:
            return Response({
                "success": False,
                "message": "Async PDF generation is only supported for 'attendance-summary' and 'department-summary'."
            }, status=400)
