# 1.  Check whether a number is even or odd. 
# def evenOdd():
#     try:
#         num = int(input("Enter the number : "))
#         if num%2==0:
#             print("Even number")
#         else:
#             print("Odd number")
#     except ValueError:
#         print("Enter a vaid number ")
# evenOdd()



# 2. Find the largest of three numbers. 
# def max():
#     try:
#         num1=int(input("enter the first number : "))
#         num2=int(input("Enter the second number : "))
#         num3=int(input("Enter the third number : "))
#         if num1>num2 and num1>num3:
#             print(f"first number is the largest number")
#         elif num2>num3:
#             print(f"second number is the largest number")
#         else:
#             print(f"third number is the largest number")
#     except ValueError:
#         print("Enter a valid number")
# max()

# 3. Reverse a string. 
# def reverseString():
#     str = input("Enter a string : ")
#     reverse = str[::-1]
#     print(reverse)
# reverseString()

#  Count vowels in a string. 
# def vowelCount():
#     vowels = ['A','E','I','O','U','a','e','i','o','u']
#     count = 0
#     str = input("Enter the string : ")
#     for i in str:
#         if i in vowels:
#             count+=1
#     if count == 0 :
#         print(f"No vowels presnt in the given string : {str}")
#     else:
#         print(f"the total number of vowels present in gien string {str} : {count}")
# vowelCount()

#  Check a palindrome. 
# def palindrome():
#     str = input("Enter the string to check : ")
#     org_str = str
#     reverse_str = str[::-1]
#     if org_str==reverse_str:
#         print("the given string is a palindrome")
#     else:
#         print("the given string is not a palindrome")    
# palindrome()

#  Find duplicate elements in a list. 
# def duplicate_elements():
#     list = [1,2,'a','s','a',3,4,5,1,3,6,7,3]
#     dups= []
#     for i in range(len(list)):
#         for j in range(i+1,len(list)):
#             if list[i]==list[j] and list[i] not in dups:
#                 dups.append(list[i])
#     print(f"Duplicate elements : {dups}")
# duplicate_elements()

#  Sort employee salaries. 
# def sort_sal():
#     employees = {
#         'John':40000,
#         'Ben':39000,
#         'Gus':120000,
#         'Rama':30000,
#         'Sai':13000
#         }
#     sorted_sal = sorted(employees.items(), key=lambda x:x[1])
#     for name , salary in sorted_sal:
#         print(name,salary)
# sort_sal()


#  Calculate average salary from employee records.
# def avg_sal():
#     employees = {
#         'John':40000,
#         'Ben':39000,
#         'Gus':120000,
#         'Rama':30000,
#         'Sai':13000
#         }
#     sum = 0
#     avg = 0
#     for i in employees.values():
#         sum += i
#         avg = sum/len(employees.values())
#     print(f"The average salary of the employee records : {avg}")
# avg_sal()

#  Find the employee with highest salary. 
# def highest_sal():
#     employees = {
#         'John':40000,
#         'Ben':39000,
#         'Gus':120000,
#         'Rama':30000,
#         'Sai':13000
#         }
#     max_sal = 0
#     emp_name = ""
#     for name , sal in employees.items():
#         if sal>max_sal:
#             max_sal = sal
#             emp_name=name
#     print(f"The employee with highest salary is  {emp_name} : {max_sal}")
# highest_sal()

#  Generate a simple salary slip. 
def salary_slip():
    name = input("Enter employee name: ")
    salary = float(input("Enter salary: "))
    allowance = float(input("Enter allowance: "))
    deduction = float(input("Enter deduction: "))

    net_salary = salary + allowance - deduction

    print("\nSALARY SLIP")
    print("-----------")
    print("Employee Name :", name)
    print("Basic Salary  :", salary)
    print("Allowance     :", allowance)
    print("Deduction     :", deduction)
    print("Net Salary    :", net_salary)

salary_slip()