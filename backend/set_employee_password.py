
from getpass import getpass

from app.database import SessionLocal
from app.models import Employee
from app.security import hash_password


db = SessionLocal()

try:
    email = input("Enter employee email: ").strip().lower()

    employee = db.query(Employee).filter(
        Employee.email == email
    ).first()

    if employee is None:
        print("Employee not found.")
    else:
        password = getpass("Enter new password: ")
        confirm_password = getpass("Confirm password: ")

        if len(password) < 8:
            print("Password must contain at least 8 characters.")
        elif password != confirm_password:
            print("Passwords do not match.")
        else:
            employee.password_hash = hash_password(password)
            db.commit()
            print("Employee password updated successfully.")

except Exception as error:
    db.rollback()
    print("Error:", error)

finally:
    db.close()

