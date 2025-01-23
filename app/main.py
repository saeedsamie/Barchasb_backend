from fastapi import FastAPI

from app.routers import users_router, tasks_router

app = FastAPI()

app.include_router(users_router.router, prefix="/api/v1/users", tags=["users"])
app.include_router(tasks_router.router, prefix="/api/v1/tasks", tags=["tasks"])
# app.include_router(leaderboard.router, prefix="/api/v1/leaderboard", tags=["leaderboard"])

# Example tasks for demonstration
tasks_db = {
    1: {"id": 1, "title": "Label Images", "description": "Label a set of images for object detection",
        "total_labels": 0},
    2: {"id": 2, "title": "Transcribe Audio", "description": "Transcribe audio recordings to text", "total_labels": 0}
}


@app.get("/")
def root():
    return {"message": "Welcome to Barchasb Backend!"}
