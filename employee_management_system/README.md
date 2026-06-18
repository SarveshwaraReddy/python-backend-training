# Employee Management System

A role-based employee management console application demonstrating advanced Python concepts, decorators, logging, and reporting.

## Setup

1. Create and activate a virtual environment:

   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

## Run

From the parent directory (`Backend-training`):

```powershell
python -m employee_management_system.main
```

## Features

- Role-based access: Admin, HR, Employee
- Custom decorators for authorization
- Logging to `logs/application.log` and `logs/errors.log`
- Employee CRUD operations
- Employee reports: total count, department breakdown, highest salary, averages
- Data persisted in JSON files under `data/`

## Project structure

- `models/` — Employee and User data models
- `services/` — Business logic for employees, authentication, and reporting
- `decorators/` — Permission decorators
- `utils/` — Logger configuration
- `data/` — JSON data stores
- `logs/` — Application and error logs
