
from typing import Literal
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


# Existing progress validation
class TaskProgressCreate(BaseModel):
    progress_percentage: int = Field(ge=0, le=100)
    update_text: str = Field(min_length=1, max_length=2000)



# Employee creation
class EmployeeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=150)
    password: str = Field(min_length=8, max_length=128)
    department: str | None = Field(default=None, max_length=100)
    role: Literal["admin", "employee"] = "employee"
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()

        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Enter a valid email address")

        return value

# Employee updating
class EmployeeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: str | None = Field(default=None, min_length=5, max_length=150)
    department: str | None = Field(default=None, max_length=100)
    role: Literal["admin", "employee"] | None = None
    is_active: bool | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if value is None:
            return value

        value = value.strip().lower()

        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Enter a valid email address")

        return value


# Task creation
class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str | None = None
    assigned_to: int = Field(gt=0)
    status: Literal["pending", "in_progress", "completed"] = "pending"
    priority: Literal["low", "medium", "high"] = "medium"
    due_date: datetime | None = None


# Task updating
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = None
    assigned_to: int | None = Field(default=None, gt=0)
    status: Literal["pending", "in_progress", "completed"] | None = None
    priority: Literal["low", "medium", "high"] | None = None
    due_date: datetime | None = None

# Employee login
class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=150)
    password: str = Field(min_length=8, max_length=128)


# Authentication token response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Logged-in employee information
class CurrentEmployee(BaseModel):
    id: int
    name: str
    email: str
    role: str






