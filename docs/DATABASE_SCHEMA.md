# Database Schema

## Database
- Name: employee_task_management
- Engine: PostgreSQL

## Employees Table
Stores employee and administrator information.

| Column | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| name | VARCHAR(100) | Employee name |
| email | VARCHAR(150) | Unique email |
| password_hash | VARCHAR(255) | Hashed password |
| department | VARCHAR(100) | Department |
| role | VARCHAR(20) | admin or employee |
| is_active | Boolean | Account status |
| created_at | DateTime | Creation timestamp |

## Tasks Table
Stores tasks assigned to employees.

| Column | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| title | VARCHAR(150) | Task title |
| description | Text | Task details |
| assigned_to | Integer | Foreign key to employees.id |
| status | VARCHAR(20) | Task status |
| priority | VARCHAR(20) | Task priority |
| due_date | DateTime | Optional due date |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

## Task Progress Table
Stores progress updates for tasks.

| Column | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| task_id | Integer | Foreign key to tasks.id |
| employee_id | Integer | Optional foreign key to employees.id |
| progress_percentage | Integer | Progress from 0 to 100 |
| update_text | Text | Progress description |
| created_at | DateTime | Update timestamp |

## Relationships
- One employee can have multiple assigned tasks.
- Each task is assigned to an employee.
- One task can have multiple progress updates.
- Each progress update belongs to a task.
- A progress update can reference its employee.

## Task Values
Statuses: pending, in_progress, completed.

Priorities: low, medium, high.

Progress percentage: 0 to 100.

## Database Initialization
Run from the backend directory: python create_tables.py
