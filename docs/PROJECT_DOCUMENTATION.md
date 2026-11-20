# Project Documentation

## 1. Project Overview

The Employee Task Management System is a web application designed to help administrators manage employees and tasks while allowing employees to track and update their assigned work.

## 2. Objectives

- Centralize employee and task management.
- Allow administrators to assign tasks to employees.
- Track task status and progress.
- Maintain a history of progress updates.
- Provide productivity and performance reports.

## 3. User Roles

### Admin
- Access the administrative dashboard.
- Manage employee records.
- Create, assign, update, and delete tasks.
- Monitor task progress.
- View productivity reports.

### Employee
- Log in to the application.
- View assigned tasks.
- Update task status and progress.
- View previous progress updates.

## 4. Application Architecture

### Frontend
React and JavaScript provide the user interface. Vite is used for frontend development and building.

### Backend
FastAPI provides REST API endpoints, request validation, authentication, authorization, and application logic.

### Database
PostgreSQL stores employee information, tasks, and progress updates. SQLAlchemy is used for database operations.

## 5. Main Workflows

### Authentication
1. User submits login credentials.
2. Backend verifies the credentials.
3. Backend returns a JWT token.
4. Frontend uses the token for authenticated API requests.

### Task Management
1. Admin creates a task.
2. Admin assigns the task to an employee.
3. Employee views the assigned task.
4. Employee submits progress updates.
5. Admin monitors the updated progress.

### Reporting
Administrators can view dashboard information, employee performance, and weekly progress reports.

## 6. Security

- Passwords are stored as hashes.
- JWT is used for authentication.
- Role-based authorization restricts administrative operations.
- Environment variables are used for configuration and secrets.

## 7. Configuration

Backend configuration is maintained in the root `.env` file. Frontend configuration is maintained in `frontend/.env`.

Use the corresponding `.env.example` templates when setting up the project.

## 8. Scope

The project covers local application development and functionality. Deployment is not included.
