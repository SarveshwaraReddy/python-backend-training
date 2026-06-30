-- Module 5: Advanced SQL & Module 6: Joins - Reports & Analysis

-- 1. Highest-paid employee
SELECT * FROM employees_employee 
ORDER BY salary DESC 
LIMIT 1;

-- 2. Lowest-paid employee
SELECT * FROM employees_employee 
ORDER BY salary ASC 
LIMIT 1;

-- 3. Average salary by department
SELECT d.name AS department_name, AVG(e.salary) AS average_salary
FROM employees_employee e
JOIN departments_department d ON e.department_id = d.id
GROUP BY d.name;

-- 4. Employees joined this year
SELECT * FROM employees_employee
WHERE EXTRACT(YEAR FROM joining_date) = EXTRACT(YEAR FROM CURRENT_DATE);

-- 5. Top 10 highest salaries
SELECT * FROM employees_employee 
ORDER BY salary DESC 
LIMIT 10;

-- 6. Total employees per department
SELECT d.name AS department_name, COUNT(e.id) AS total_employees
FROM departments_department d
LEFT JOIN employees_employee e ON e.department_id = d.id
GROUP BY d.name;

-- 7. Departments with more than 20 employees
SELECT d.name AS department_name, COUNT(e.id) AS total_employees
FROM departments_department d
JOIN employees_employee e ON e.department_id = d.id
GROUP BY d.name
HAVING COUNT(e.id) > 20;

-- 8. Employees with salary above department average
SELECT e.employee_id, e.first_name, e.last_name, e.salary, d.name AS department_name
FROM employees_employee e
JOIN departments_department d ON e.department_id = d.id
WHERE e.salary > (
    SELECT AVG(emp.salary)
    FROM employees_employee emp
    WHERE emp.department_id = e.department_id
);

-- 9. Employee + Department report (INNER JOIN)
SELECT e.employee_id, e.first_name, e.last_name, e.designation, e.salary, d.name AS department_name
FROM employees_employee e
INNER JOIN departments_department d ON e.department_id = d.id;

-- 10. Employee + Payroll report (LEFT JOIN)
SELECT e.employee_id, e.first_name, e.last_name, p.month, p.net_salary
FROM employees_employee e
LEFT JOIN payroll_payroll p ON e.id = p.employee_id;

-- 11. Employee + Attendance report (LEFT JOIN)
SELECT e.employee_id, e.first_name, e.last_name, a.date, a.status AS attendance_status
FROM employees_employee e
LEFT JOIN attendance_attendance a ON e.id = a.employee_id;
