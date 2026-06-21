-- Schema permissions for Django (run on employee_management database)
-- PostgreSQL 15+ requires explicit public schema grants

GRANT ALL ON SCHEMA public TO employee_admin;
GRANT CREATE ON SCHEMA public TO employee_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO employee_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO employee_admin;
