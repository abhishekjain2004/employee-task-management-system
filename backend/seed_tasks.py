
from app.database import SessionLocal
from app.models import Task

db = SessionLocal()

tasks = [
    {
        "title": "Prepare Sales Report",
        "description": "Prepare the monthly sales performance report.",
        "assigned_to": 2,
        "status": "pending",
        "priority": "high"
    },
    {
        "title": "Update Power BI Dashboard",
        "description": "Update the sales dashboard with recent data.",
        "assigned_to": 3,
        "status": "in_progress",
        "priority": "medium"
    },
    {
        "title": "Database Maintenance",
        "description": "Check database performance and clean unused records.",
        "assigned_to": 2,
        "status": "pending",
        "priority": "low"
    },
    {
        "title": "Analyze Customer Data",
        "description": "Analyze customer trends and prepare insights.",
        "assigned_to": 3,
        "status": "in_progress",
        "priority": "high"
    }
]

try:
    for task_data in tasks:

        existing_task = db.query(Task).filter(
            Task.title == task_data["title"],
            Task.assigned_to == task_data["assigned_to"]
        ).first()

        if existing_task is None:
            task = Task(**task_data)
            db.add(task)

    db.commit()

    print("Sample tasks inserted successfully!")

except Exception as error:
    db.rollback()
    print("Error:", error)

finally:
    db.close()
