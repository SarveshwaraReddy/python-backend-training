from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db import connection
from api.responses.custom_response import SuccessResponse

class RawSQLReportsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, report_type=None):
        # Allow ADMIN and HR roles to view reports
        if request.user.role not in ['ADMIN', 'HR']:
            return Response({"success": False, "message": "Permission Denied"}, status=403)

        if report_type == 'top-salaries':
            query = """
                SELECT employee_id, first_name, last_name, salary, designation
                FROM employees_employee
                ORDER BY salary DESC
                LIMIT 10;
            """
            data = self.execute_query(query)
            return SuccessResponse(data=data, message="Top salary report generated successfully")

        elif report_type == 'department-summary':
            query = """
                SELECT d.name AS department_name, 
                       COUNT(e.id) AS total_employees,
                       COALESCE(AVG(e.salary), 0.0) AS average_salary
                FROM departments_department d
                LEFT JOIN employees_employee e ON e.department_id = d.id
                GROUP BY d.name;
            """
            data = self.execute_query(query)
            return SuccessResponse(data=data, message="Department summary report generated successfully")

        elif report_type == 'monthly-payroll':
            query = """
                SELECT month, 
                       COUNT(id) AS employees_paid, 
                       SUM(net_salary) AS total_paid
                FROM payroll_payroll
                GROUP BY month
                ORDER BY month DESC;
            """
            data = self.execute_query(query)
            return SuccessResponse(data=data, message="Monthly payroll report generated successfully")

        elif report_type == 'attendance-summary':
            query = """
                SELECT e.employee_id, e.first_name, e.last_name, 
                       a.date, a.status
                FROM employees_employee e
                INNER JOIN attendance_attendance a ON e.id = a.employee_id
                ORDER BY a.date DESC;
            """
            data = self.execute_query(query)
            return SuccessResponse(data=data, message="Attendance report generated successfully")

        else:
            return Response({
                "success": False,
                "message": "Invalid report type. Choose top-salaries, department-summary, monthly-payroll, or attendance-summary."
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

    def execute_query(self, query):
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
