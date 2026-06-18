employees = []

while True:
    print("\n*** EMPLOYEE MANAGEMENT SYSTEM ***")
    print("1. Add Employee")
    print("2. View All Employees")
    print("3. Search Employee by ID")
    print("4. Update Employee Details")
    print("5. Delete Employee")
    print("6. Exit")
    
    choice = input("Enter your choice (1-6): ")
    # Add Employee Feature
    if choice == "1":
        print("\n--- Add Employee ---")
        try:
            emp_id = int(input("Enter Employee ID: "))
        except ValueError:
            print("Invalid input! ID must be a number.")
            continue
            
        id_exists = False
        for emp in employees:
            if emp["Employee ID"] == emp_id:
                id_exists = True
                break
        
        if id_exists == True:
            print("Error: This ID already exists!")
        else:
            name = input("Enter Name: ")
            email = input("Enter Email: ")
            dept = input("Enter Department: ")
            
            try:
                salary = float(input("Enter Salary: "))
                exp = float(input("Enter Experience: "))
            except ValueError:
                print("Invalid salary or experience! Setting them to 0.")
                salary = 0.0
                exp = 0.0
                
            new_emp = {
                "Employee ID": emp_id,
                "Name": name,
                "Email": email,
                "Department": dept,
                "Salary": salary,
                "Experience": exp
            }
            employees.append(new_emp)
            print("Employee added successfully!")
            
    # View all employees
    
    elif choice == "2":
        print("\n--- View All Employees ---")
        if len(employees) == 0:
            print("No employees found.")
        else:
          
            for emp in employees:
                print("ID:", emp["Employee ID"], "| Name:", emp["Name"], "| Email:", emp["Email"], "| Dept:", emp["Department"], "| Salary:", emp["Salary"], "| Exp:", emp["Experience"])


    # Search Employee
   
    elif choice == "3":
        print("\n--- Search Employee ---")
        try:
            search_id = int(input("Enter Employee ID to search: "))
        except ValueError:
            print("Please enter a valid number ID.")
            continue
            
        found = False
        for emp in employees:
            if emp["Employee ID"] == search_id:
                print("Employee Found!")
                print("ID:", emp["Employee ID"])
                print("Name:", emp["Name"])
                print("Email:", emp["Email"])
                print("Department:", emp["Department"])
                print("Salary:", emp["Salary"])
                print("Experience:", emp["Experience"])
                found = True
                break
                
        if found == False:
            print("Employee not found.")

 # UPDATE EMPLOYEE

    elif choice == "4":
        print("\n--- Update Employee ---")
        try:
            update_id = int(input("Enter Employee ID to update: "))
        except ValueError:
            print("Please enter a valid number ID.")
            continue
            
        found = False
        for emp in employees:
            if emp["Employee ID"] == update_id:
                found = True
                print("Leave blank if you don't want to change the value.")
                
                new_name = input("Enter New Name: ")
                if new_name != "":
                    emp["Name"] = new_name
                    
                new_email = input("Enter New Email: ")
                if new_email != "":
                    emp["Email"] = new_email
                    
                new_dept = input("Enter New Department: ")
                if new_dept != "":
                    emp["Department"] = new_dept
                    
                new_salary = input("Enter New Salary: ")
                if new_salary != "":
                    try:
                        emp["Salary"] = float(new_salary)
                    except ValueError:
                        print("Invalid number! Salary not changed.")
                        
                new_exp = input("Enter New Experience: ")
                if new_exp != "":
                    try:
                        emp["Experience"] = float(new_exp)
                    except ValueError:
                        print("Invalid number! Experience not changed.")
                        
                print("Employee updated successfully!")
                break
                
        if found == False:
            print("Employee not found.")

    #  Delete Employee
  
    elif choice == "5":
        print("\n--- Delete Employee ---")
        try:
            delete_id = int(input("Enter Employee ID to delete: "))
        except ValueError:
            print("Please enter a valid number ID.")
            continue
            
        found = False
        for emp in employees:
            if emp["Employee ID"] == delete_id:
                employees.remove(emp)
                print("Employee deleted successfully!")
                found = True
                break
                
        if found == False:
            print("Employee not found.")

    #  Exit
    elif choice == "6":
        print("Thank you for using the application. Bye!")
        break
        
    else:
        print("Invalid choice! Please choose between 1 and 6.")