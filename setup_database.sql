-- PostgreSQL setup for Employee Management System
-- Run this file as the postgres superuser

-- Create database if it does not exist
SELECT 'CREATE DATABASE employee_management'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'employee_management')\gexec

-- Create or reset the application user
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'employee_admin') THEN
        CREATE USER employee_admin WITH PASSWORD 'password123';
    ELSE
        ALTER USER employee_admin WITH PASSWORD 'password123';
    END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE employee_management TO employee_admin;
