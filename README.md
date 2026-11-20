# Employee Task Management System

A web-based application for managing employees, assigning tasks, tracking task progress, and viewing productivity reports.

## Features

### Admin
- View dashboard overview and productivity reports.
- Create, view, update, and delete employees.
- Create, assign, update, and delete tasks.
- Change task status and monitor employee progress.
- View employee performance and weekly progress.

### Employee
- Log in securely.
- View assigned tasks.
- Update task progress with a percentage and description.
- View progress update history.

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, JavaScript, Vite |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Authentication | JWT |

## Project Structure

- `backend/` - FastAPI application and database logic.
- `frontend/` - React user interface.
- `docs/` - Project, database, and API documentation.
- `requirements.txt` - Python dependencies.
- `.env.example` - Backend environment variable template.

## Local Setup

### Prerequisites
- Python 3.10 or later
- Node.js and npm
- PostgreSQL

### Backend
1. Create and activate a Python virtual environment.
2. Install dependencies using `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and configure database credentials and JWT secret.
4. Create a PostgreSQL database named `employee_task_management`.
5. From the `backend/` directory, run `python create_tables.py`.
6. Optionally run `python seed_data.py` and `python seed_tasks.py` to insert sample records.
7. Use `python set_employee_password.py` to set passwords for sample employees.
8. Start the API using `uvicorn app.main:app --reload`.

Backend URL: `http://127.0.0.1:8000`

API documentation: `http://127.0.0.1:8000/docs`

### Frontend
1. Open another terminal and enter the `frontend/` directory.
2. Copy `.env.example` to `.env`.
3. Install dependencies using `npm install`.
4. Start the frontend using `npm run dev`.

Frontend URL: `http://localhost:5173`

## Security
- Passwords are stored as hashes.
- API authentication uses JWT tokens.
- Role-based access controls protect administrative operations.
- Environment files containing credentials must not be committed.

## Project Status
The main application workflows have been developed and checked locally. Deployment is outside the current project scope.
