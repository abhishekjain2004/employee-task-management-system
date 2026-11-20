
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    department = Column(String(100), nullable=True)
    role = Column(String(20), nullable=False, default="employee")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)

    assigned_to = Column(Integer, ForeignKey("employees.id"), nullable=False)

    status = Column(String(20), nullable=False, default="pending")
    priority = Column(String(20), nullable=False, default="medium")

    due_date = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())



class TaskProgress(Base):
    __tablename__ = "task_progress"

    id = Column(Integer, primary_key=True, index=True)

    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=True
    )

    progress_percentage = Column(Integer, nullable=False, default=0)
    update_text = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())




