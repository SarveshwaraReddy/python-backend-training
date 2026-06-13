# Employee Management Console

A simple Python console application for managing employee records.

## Description

This program provides a text-based employee management system. It keeps employee data in memory using a list of dictionaries and allows the user to perform the following operations:

- Add a new employee record
- View all employees
- Search for an employee by ID
- Update an employee's details
- Delete an employee record
- Exit the application

## How it works

The program displays a numbered menu and reads the user's choice in a loop. Based on the selected option, it:

1. Prompts for employee details and adds a new entry.
2. Prints all employee records stored in memory.
3. Finds and displays a record by employee ID.
4. Lets the user update selected fields for an existing employee.
5. Removes an employee entry by ID.
6. Stops the program.

The program validates numeric input for IDs, salary, and experience, and prevents duplicate employee IDs.

## Run the program

From the workspace root, run:

```bash
python Python-Practice/EmployeeManagementConsole.py
```

Then follow the menu prompts in the terminal.
