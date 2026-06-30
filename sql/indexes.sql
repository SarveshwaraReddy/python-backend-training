-- Database Indexing for Employee Management System

-- Single-column index on joining_date
CREATE INDEX idx_employee_joining_date ON employees_employee(joining_date);

-- Single-column index on salary
CREATE INDEX idx_employee_salary ON employees_employee(salary);

-- Multi-column index on department_id and salary
CREATE INDEX idx_department_salary ON employees_employee(department_id, salary);
