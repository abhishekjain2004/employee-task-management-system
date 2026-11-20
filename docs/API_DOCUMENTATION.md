# API Documentation

Base URL: http://127.0.0.1:8000

Interactive API reference: http://127.0.0.1:8000/docs

## Authentication

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| POST | /auth/login | Public | User login |
| GET | /auth/me | Authenticated | Get current user |

Authenticated requests use a JWT bearer token.

## General

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | / | Public | Application information |
| GET | /health | Public | Health check |

## Employees

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | /employees | Admin | List employees |
| GET | /employees/{employee_id} | Authenticated | Get employee |
| POST | /employees | Admin | Create employee |
| PUT | /employees/{employee_id} | Admin | Update employee |
| DELETE | /employees/{employee_id} | Admin | Delete employee |
| GET | /employees/{employee_id}/tasks | Authenticated | Get employee tasks |

## Tasks

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | /tasks | Authenticated | List permitted tasks |
| GET | /tasks/with-employees | Admin | List tasks with employee details |
| POST | /tasks | Admin | Create task |
| PUT | /tasks/{task_id} | Admin | Update task |
| DELETE | /tasks/{task_id} | Admin | Delete task |
| PUT | /tasks/{task_id}/status | Admin | Update task status |
| PUT | /tasks/{task_id}/assign | Admin | Assign task to employee |

## Task Progress

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | /tasks/{task_id}/progress | Assigned-task access | View progress history |
| POST | /tasks/{task_id}/progress | Assigned-task access | Submit progress update |

## Reports

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | /reports/overview | Admin | Dashboard summary |
| GET | /reports/employee-performance | Admin | Employee performance |
| GET | /reports/weekly-progress?days=7 | Admin | Weekly progress report |

## Common Values

Task statuses:
- pending
- in_progress
- completed

Task priorities:
- low
- medium
- high

Progress percentage: 0 to 100.

## Authorization

- Public endpoints do not require login.
- Authenticated endpoints require a valid JWT token.
- Admin endpoints require administrator access.
- Task progress operations are subject to task access permissions.

Note: Refer to the running FastAPI Swagger documentation at `/docs` for exact request fields, response formats, and validation requirements.
