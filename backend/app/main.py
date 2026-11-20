from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee, Task, TaskProgress

from dotenv import load_dotenv

from datetime import datetime, timedelta, timezone
from fastapi import Query
from sqlalchemy import func, case

import os
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.schemas import (
    TaskProgressCreate,
    EmployeeCreate,
    EmployeeUpdate,
    TaskCreate,
    TaskUpdate
)

from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_employee,
    get_current_admin
)

from app.schemas import LoginRequest, TokenResponse, CurrentEmployee



app = FastAPI(
    title="Employee Task Management System",
    description="API for managing employees, tasks, and daily progress.",
    version="1.0.0"
)

load_dotenv()

FRONTEND_URL = (
    os.getenv("FRONTEND_URL") or "http://localhost:5173"
).strip().rstrip("/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def check_task_access(task: Task, employee: Employee):
    if employee.role != "admin" and task.assigned_to != employee.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this task"
        )

# Employee Login API
@app.post("/auth/login", response_model=TokenResponse)
def employee_login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    email = login_data.email.strip().lower()
    employee = db.query(Employee).filter(
        Employee.email == email
    ).first()
    
    if (
        employee is None
        or not employee.is_active
        or not employee.password_hash
        or not verify_password(
            login_data.password,
            employee.password_hash
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={"sub": str(employee.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# Get Logged-in Employee
@app.get("/auth/me", response_model=CurrentEmployee)
def get_logged_in_employee(
    current_employee: Employee = Depends(get_current_employee)
):
    return current_employee



@app.get("/")
def root():
    return {
        "message": "Employee Task Management System API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/employees")
def get_employees(db: Session = Depends(get_db),
                   current_admin: Employee = Depends(get_current_admin)
                   ):

    employees = db.query(Employee).all()

    return [
        {
            "id": employee.id,
            "name": employee.name,
            "email": employee.email,
            "department": employee.department,
            "role": employee.role,
            "is_active": employee.is_active,
            "created_at": employee.created_at
        }
        for employee in employees
    ]


@app.get("/employees/{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_db),
                 current_employee: Employee = Depends(get_current_employee)
                 ):

    if current_employee.role != "admin" and employee_id != current_employee.id:
        raise HTTPException(
        status_code=403,
        detail="You can only view your own employee details"
    )

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return {
        "id": employee.id,
        "name": employee.name,
        "email": employee.email,
        "department": employee.department,
        "role": employee.role,
        "is_active": employee.is_active,
        "created_at": employee.created_at
    }

@app.get("/tasks")
def get_tasks(
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee)
):
    query = db.query(Task)

    if current_employee.role != "admin":
        query = query.filter(Task.assigned_to == current_employee.id)

    tasks = query.all()

    return [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "assigned_to": task.assigned_to,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "created_at": task.created_at
        }
        for task in tasks
    ]


@app.get("/tasks/with-employees")
def get_tasks_with_employees(db: Session = Depends(get_db),
                             current_admin: Employee = Depends(get_current_admin)
                             ):

    results = db.query(Task, Employee.name).join(
        Employee,
        Task.assigned_to == Employee.id
    ).all()

    return [
        {
            "task_id": task.id,
            "title": task.title,
            "employee_name": employee_name,
            "status": task.status,
            "priority": task.priority
        }
        for task, employee_name in results
    ]


@app.get("/employees/{employee_id}/tasks")
def get_employee_tasks(employee_id: int, db: Session = Depends(get_db),
                       current_employee: Employee = Depends(get_current_employee)
                       ):
    if current_employee.role != "admin" and employee_id != current_employee.id:
        raise HTTPException(
        status_code=403,
        detail="You can only view your own tasks"
    )

    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    tasks = db.query(Task).filter(
        Task.assigned_to == employee_id
    ).all()

    return [
        {
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority
        }
        for task in tasks
    ]




@app.get("/tasks/{task_id}/progress")
def get_task_progress(
    task_id: int,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee)
):
    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    check_task_access(task, current_employee)

    progress_records = db.query(TaskProgress).filter(
        TaskProgress.task_id == task_id
    ).all()

    return [
        {
            "id": progress.id,
            "task_id": progress.task_id,
            "progress_percentage": progress.progress_percentage,
            "update_text": progress.update_text,
            "created_at": progress.created_at
        }
        for progress in progress_records
    ]



@app.post("/tasks/{task_id}/progress", status_code=201)
def add_task_progress(
    task_id: int,
    progress_data: TaskProgressCreate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee)
):
    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    check_task_access(task, current_employee)

    progress = TaskProgress(
        task_id=task_id,
        employee_id=current_employee.id,
        progress_percentage=progress_data.progress_percentage,
        update_text=progress_data.update_text
        
    )

    try:
        db.add(progress)
        db.commit()
        db.refresh(progress)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while adding task progress"
        )

    return {
        "message": "Progress added successfully",
        "id": progress.id,
        "task_id": progress.task_id,
        "progress_percentage": progress.progress_percentage,
        "update_text": progress.update_text,
        "created_at": progress.created_at
    }


@app.put("/tasks/{task_id}/status")
def update_task_status(
    task_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_admin: Employee = Depends(get_current_admin)
):
    allowed_statuses = ["pending", "in_progress", "completed"]

    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Use pending, in_progress, or completed"
        )

    try:
        task.status = status
        db.commit()
        db.refresh(task)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while updating task status"
        )

    return {
        "message": "Task status updated successfully",
        "task_id": task.id,
        "status": task.status
    }



@app.put("/tasks/{task_id}/assign")
def assign_task(
    task_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    current_admin: Employee = Depends(get_current_admin)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.is_active == True
    ).first()

    if employee is None:
        raise HTTPException(status_code=404, detail="Active employee not found")

    try:
        task.assigned_to = employee_id
        db.commit()
        db.refresh(task)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while assigning task"
        )

    return {
        "message": "Task assigned successfully",
        "task_id": task.id,
        "assigned_to": employee.id,
        "employee_name": employee.name
    }


# 1. Overall dashboard summary
@app.get("/reports/overview")
def get_report_overview(db: Session = Depends(get_db),
                        current_admin: Employee = Depends(get_current_admin)
                        ):

    total_employees = db.query(Employee).count()

    active_employees = db.query(Employee).filter(
        Employee.is_active == True
    ).count()

    total_tasks = db.query(Task).count()

    pending_tasks = db.query(Task).filter(
        Task.status == "pending"
    ).count()

    in_progress_tasks = db.query(Task).filter(
        Task.status == "in_progress"
    ).count()

    completed_tasks = db.query(Task).filter(
        Task.status == "completed"
    ).count()

    total_updates = db.query(TaskProgress).count()

    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "in_progress_tasks": in_progress_tasks,
        "completed_tasks": completed_tasks,
        "total_progress_updates": total_updates
    }


# 2. Employee-wise task performance
@app.get("/reports/employee-performance")
def get_employee_performance(db: Session = Depends(get_db),
                             current_admin: Employee = Depends(get_current_admin)
                             ):

    results = db.query(
        Employee.id,
        Employee.name,
        func.count(Task.id).label("total_tasks"),

        func.coalesce(
            func.sum(
                case((Task.status == "completed", 1), else_=0)
            ), 0
        ).label("completed_tasks"),

        func.coalesce(
            func.sum(
                case((Task.status == "pending", 1), else_=0)
            ), 0
        ).label("pending_tasks"),

        func.coalesce(
            func.sum(
                case((Task.status == "in_progress", 1), else_=0)
            ), 0
        ).label("in_progress_tasks")

    ).outerjoin(
        Task, Task.assigned_to == Employee.id
    ).group_by(
        Employee.id, Employee.name
    ).all()

    return [
        {
            "employee_id": row.id,
            "employee_name": row.name,
            "total_tasks": row.total_tasks,
            "completed_tasks": row.completed_tasks,
            "pending_tasks": row.pending_tasks,
            "in_progress_tasks": row.in_progress_tasks
        }
        for row in results
    ]


# 3. Daily/weekly productivity report
@app.get("/reports/weekly-progress")
def get_weekly_progress(
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_admin: Employee = Depends(get_current_admin)

):

    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    results = db.query(
        TaskProgress,
        Task.title,
        Employee.name
    ).join(
        Task, TaskProgress.task_id == Task.id
    ).join(
        Employee, TaskProgress.employee_id == Employee.id
    ).filter(
        TaskProgress.created_at >= start_date
    ).order_by(
        TaskProgress.created_at.desc()
    ).all()

    return {
        "report_period_days": days,
        "total_updates": len(results),
        "updates": [
            {
                "task_id": progress.task_id,
                "task_title": task_title,
                "employee_name": employee_name,
                "progress_percentage": progress.progress_percentage,
                "update_text": progress.update_text,
                "created_at": progress.created_at
            }
            for progress, task_title, employee_name in results
        ]
    }




# ==========================================
# EMPLOYEE CRUD
# ==========================================

# 1. Create employee

@app.post("/employees", status_code=201)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_admin: Employee = Depends(get_current_admin)
):
    employee = Employee(
        name=employee_data.name,
        email=employee_data.email.strip().lower(),
        password_hash=hash_password(employee_data.password),
        department=employee_data.department,
        role=employee_data.role
    )

    try:
        db.add(employee)
        db.commit()
        db.refresh(employee)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="An employee with this email already exists"
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while creating employee"
        )

    return {
        "message": "Employee created successfully",
        "id": employee.id,
        "name": employee.name,
        "email": employee.email,
        "department": employee.department,
        "role": employee.role
    }


# 2. Update employee

@app.put("/employees/{employee_id}")
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_admin: Employee = Depends(get_current_admin)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = employee_data.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] is not None:
        update_data["email"] = update_data["email"].strip().lower()


    if employee.id == current_admin.id:
        if update_data.get("role") not in (None, "admin") or update_data.get("is_active") is False:
            raise HTTPException(
            status_code=400,
            detail="You cannot remove your own admin access or deactivate your account"
        )


    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update"
        )

    for key, value in update_data.items():
        if value is None and key != "department":
            raise HTTPException(
                status_code=422,
                detail=f"{key} cannot be null"
            )

        setattr(employee, key, value)

    try:
        db.commit()
        db.refresh(employee)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email already belongs to another employee"
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while updating employee"
        )

    return {
        "message": "Employee updated successfully",
        "id": employee.id,
        "name": employee.name,
        "email": employee.email,
        "department": employee.department,
        "role": employee.role,
        "is_active": employee.is_active
    }


# 3. Deactivate employee (soft delete)

@app.delete("/employees/{employee_id}")
def deactivate_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_admin: Employee = Depends(get_current_admin)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    if employee.id == current_admin.id:
        raise HTTPException(
        status_code=400,
        detail="You cannot deactivate your own admin account"
    )

    try:
        employee.is_active = False
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while deactivating employee"
        )

    return {
        "message": "Employee deactivated successfully",
        "employee_id": employee.id,
        "is_active": employee.is_active
    }


# ==========================================
# TASK CRUD
# ==========================================

# 4. Create task

@app.post("/tasks", status_code=201)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_admin: Employee = Depends(get_current_admin)
):
    employee = db.query(Employee).filter(
        Employee.id == task_data.assigned_to,
        Employee.is_active == True
    ).first()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Active employee not found"
        )

    task = Task(
        title=task_data.title,
        description=task_data.description,
        assigned_to=task_data.assigned_to,
        status=task_data.status,
        priority=task_data.priority,
        due_date=task_data.due_date
    )

    try:
        db.add(task)
        db.commit()
        db.refresh(task)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while creating task"
        )

    return {
        "message": "Task created successfully",
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "assigned_to": task.assigned_to,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date
    }

# 5. Update task

@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_admin: Employee = Depends(get_current_admin)
):
    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update"
        )

    for key, value in update_data.items():
        if value is None and key not in ["description", "due_date"]:
            raise HTTPException(
                status_code=422,
                detail=f"{key} cannot be null"
            )

    if "assigned_to" in update_data:
        employee = db.query(Employee).filter(
            Employee.id == update_data["assigned_to"],
            Employee.is_active == True
        ).first()

        if employee is None:
            raise HTTPException(
                status_code=404,
                detail="Active employee not found"
            )

    try:
        for key, value in update_data.items():
            setattr(task, key, value)

        db.commit()
        db.refresh(task)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while updating task"
        )

    return {
        "message": "Task updated successfully",
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "assigned_to": task.assigned_to,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date
    }


# 6. Delete task and its progress history


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_admin: Employee = Depends(get_current_admin)
):
    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    try:
        db.query(TaskProgress).filter(
            TaskProgress.task_id == task_id
        ).delete(synchronize_session=False)

        db.delete(task)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while deleting task"
        )

    return {
        "message": "Task and its progress history deleted successfully",
        "task_id": task_id
    }

