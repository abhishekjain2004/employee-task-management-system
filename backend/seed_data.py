
from app.database import SessionLocal
from app.models import Employee

db = SessionLocal()

employees = [
    {
        "name": "Abhishek Jain",
        "email": "abhishek@example.com",
        "department": "Data",
        "role": "admin"
    },
    {
        "name": "Rahul Sharma",
        "email": "rahul@example.com",
        "department": "IT",
        "role": "employee"
    },
    {
        "name": "Priya Verma",
        "email": "priya@example.com",
        "department": "Analytics",
        "role": "employee"
    }
]

try:
    for employee_data in employees:

        existing_employee = db.query(Employee).filter(
            Employee.email == employee_data["email"]
        ).first()

        if existing_employee is None:
            employee = Employee(**employee_data)
            db.add(employee)

    db.commit()

    print("Sample employees inserted successfully!")

except Exception as error:
    db.rollback()
    print("Error:", error)

finally:
    db.close()

