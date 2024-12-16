from fastapi import FastAPI

from app.routers import users, tasks, leaderboard

app = FastAPI()

app.include_router(users.router, prefix="/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["leaderboard"])

# Example tasks for demonstration
tasks_db = {
    1: {"id": 1, "title": "Label Images", "description": "Label a set of images for object detection",
        "total_labels": 0},
    2: {"id": 2, "title": "Transcribe Audio", "description": "Transcribe audio recordings to text", "total_labels": 0}
}


@app.get("/")
def root():
    return {"message": "Welcome to Barchasb Backend!"}
