from fastapi import FastAPI

from app.routers import users, tasks, submissions

app = FastAPI()

# Include Routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(submissions.router, prefix="/submissions", tags=["Submissions"])


@app.get("/")
def root():
    return {"message": "Welcome to Barchasb Backend!"}
