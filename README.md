# Barchasb Backend: Distributed Crowdsourcing for Multimedia Data Labeling

## Overview

**Barchasb Backend** is the backend API for the Barchasb distributed system. It is built with **FastAPI** and provides the core functionality for user management, task distribution, and data labeling through a crowdsourcing model. The backend supports scalable storage and seamless integration with the mobile application.

---

## Features

### Backend Functionality

- **User Management**:
  - Signup and Login.
  - User Session Management.
  - Signout functionality.
  - View personal performance metrics.
- **Task Management**:
  - View available tasks.
  - Submit labels for tasks.
  - Report corrupted tasks.
  - Crowdsourcing-based consensus for labels.
- **Leaderboard**:
  - Track user rankings based on points earned.
  - Rewards for accuracy and consistency.
- **Notifications**:
  - Send updates about new datasets and urgent tasks.
- **Scalable Data Storage**:
  - Store labeled datasets securely in MinIO or other storage solutions.

---

## System Architecture

The backend is designed to support the distributed labeling system:

### Core Components

- **Modular Routers**:
  - Users: Handles user registration, authentication, and profile management.
  - Tasks: Manages task distribution, submissions, and reporting.
  - Leaderboard: Provides rankings and performance metrics.
- **Storage**:
  - Supports integration with MinIO for scalable and secure dataset storage.

---

## Installation and Setup

### Prerequisites

- Python 3.8+
- MinIO (optional for production-grade storage)

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/barchasb-backend.git
   cd barchasb-backend
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:

   ```bash
   uvicorn app.main:app --reload
   ```

4. Access the API documentation:
   - Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

---

## API Endpoints

### User Management

- `POST /auth/signup` - Register a new user.
- `POST /auth/login` - Login with username and password.
- `GET /auth/me` - Get current user details.
- `POST /auth/logout` - Logout a user.

### Task Management

- `GET /tasks` - Retrieve a list of tasks.
- `GET /tasks/{task_id}` - Get details of a specific task.
- `POST /tasks/{task_id}/submit` - Submit a label for a task.
- `POST /tasks/report` - Report corrupted tasks.

### Leaderboard

- `GET /leaderboard` - View rankings of users.

---

## Contributing

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature-name"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Create a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

For inquiries or contributions, please reach out to:

- **Email:** support@barchasb.com
- **GitHub:** [Barchasb Backend Repo](https://github.com/your-repo)
