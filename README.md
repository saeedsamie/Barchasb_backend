# Barchasb Backend: Distributed Crowdsourcing for Multimedia Data Labeling

## Overview

**Barchasb Backend** is the backend API for the Barchasb distributed system. Built with **FastAPI**, it provides core functionalities for user management, task distribution, and data labeling through a crowdsourcing model. The backend supports scalable storage and seamless integration with the mobile application.

---

## Features

### Backend Functionality

- **User Management**:
    - User Registration and Authentication.
    - Profile Management.
    - View Personal Performance Metrics.
- **Task Management**:
    - Create and View Tasks.
    - Submit Labels for Tasks.
    - Report Issues with Tasks.
- **Leaderboard**:
    - View User Rankings Based on Points Earned.
- **Scalable Data Storage**:
    - Secure Storage of Labeled Datasets.

---

## System Architecture

The backend is designed to support the distributed labeling system with the following core components:

- **Modular Routers**:
    - **Users**: Handles user registration, authentication, and profile management.
    - **Tasks**: Manages task creation, distribution, submissions, and reporting.
    - **Leaderboard**: Provides user rankings and performance metrics.
- **Storage**:
    - Supports integration with scalable and secure dataset storage solutions.

---

## Installation and Setup

### Prerequisites

- Python 3.8+
- Database (e.g., PostgreSQL, MySQL, SQLite)

### Steps

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/saeedsamie/barchasb-backend.git
   cd barchasb-backend
   ```

2. **Set Up Virtual Environment**:

   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows, use `env\Scripts\activate`
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:

   Create a `.env` file in the root directory and add your environment-specific variables, such as database connection details and secret keys.

5. **Apply Database Migrations**:

   Ensure your database is set up and apply any necessary migrations.

6. **Run the Server**:

   ```bash
   uvicorn app.main:app --reload
   ```

7. **Access the API Documentation**:

   Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser to view the interactive API documentation.

---

## API Endpoints

### Task Management

- **Create a New Task**
  - **Endpoint**: `POST /tasks/new`
  - **Description**: Creates a new task.
  - **Request Body**:
    - `type` (string): The type of task.
    - `data` (string): The data associated with the task.
    - `point` (integer): The points assigned to the task.
    - `title` (string): The title of the task.
    - `description` (string): Detailed description of the task.
    - `tags` (list of strings, optional): Tags associated with the task.
    - `is_done` (boolean, optional): Status indicating if the task is completed.
  - **Response**:
    - Returns the created task with all its properties including the generated ID.

- **Fetch Task Feed**
  - **Endpoint**: `GET /tasks/feed`
  - **Description**: Retrieves a feed of available tasks for the authenticated user.
  - **Query Parameters**:
    - `limit` (integer): Maximum number of tasks to return (must be > 0).
  - **Response**:
    - List of tasks, each containing full task details including ID, type, data, points, title, description, and tags.

- **Submit Task Label**
  - **Endpoint**: `POST /tasks/submit`
  - **Description**: Submits a label for a task.
  - **Request Body**:
    - `task_id` (string): The ID of the task being labeled.
    - `content` (string): The label content.
  - **Response**:
    - `status` (string): Status of the operation.
    - `message` (string): Confirmation message with submission ID.

- **Report Task Issue**
  - **Endpoint**: `POST /tasks/report`
  - **Description**: Reports an issue with a task.
  - **Request Body**:
    - `task_id` (string): The ID of the task being reported.
    - `detail` (string): Detailed description of the issue.
  - **Response**:
    - `status` (string): Status of the operation.
    - `message` (string): Confirmation message with report ID.

- **Get User's Labeled Tasks**
  - **Endpoint**: `GET /tasks/labeled`
  - **Description**: Retrieves all tasks that have been labeled by the authenticated user.
  - **Response**:
    - List of tasks with full details including ID, type, data, points, title, description, tags, and completion status.

### User Management

- **Register a New User**
  - **Endpoint**: `POST /users/signup`
  - **Description**: Registers a new user.
  - **Request Body**:
    - `name` (string): The user's name.
    - `password` (string): The user's password.
    - `points` (integer, optional): Initial points for the user.
  - **Response**:
    - `id` (string): The unique identifier of the created user.
    - `name` (string): The name of the created user.

- **User Login**
  - **Endpoint**: `POST /users/login`
  - **Description**: Authenticates a user and returns an access token.
  - **Request Body**:
    - `name` (string): The user's name.
    - `password` (string): The user's password.
  - **Response**:
    - `access_token` (string): The JWT access token for authentication.

- **Get Leaderboard**
  - **Endpoint**: `GET /users/leaderboard`
  - **Description**: Retrieves a list of users sorted by points.
  - **Response**:
    - List of users, each containing:
      - `id` (string): User's unique identifier.
      - `name` (string): User's name.
      - `points` (integer): User's points.
      - `labeled_count` (integer): Number of tasks labeled by the user.

- **Get User Information**
  - **Endpoint**: `GET /users/user/`
  - **Description**: Retrieves the authenticated user's information.
  - **Response**:
    - `id` (string): The user's unique identifier.
    - `name` (string): The user's name.
    - `points` (integer): The user's points.
    - `label_count` (integer): Number of tasks labeled by the user.

- **Update User Information**
  - **Endpoint**: `PUT /users/user/`
  - **Description**: Updates the authenticated user's information.
  - **Request Body**:
    - `new_name` (string): The new name for the user.
  - **Response**:
    - Updated user information including ID, name, points, and label count.

- **Change User Password**
  - **Endpoint**: `PUT /users/user/password`
  - **Description**: Changes the authenticated user's password.
  - **Request Body**:
    - `new_password` (string): The new password.
  - **Response**:
    - `id` (string): The user's ID.
    - `result` (string): Confirmation message.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

For inquiries or contributions, please reach out to:

- **Email:** support@barchasb.com
- **GitHub:** [Barchasb Backend Repo](https://github.com/saeedsamie)

