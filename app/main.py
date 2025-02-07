from fastapi import FastAPI

from app.DatabaseManager import DatabaseManager
from app.routers import users_router, tasks_router

app = FastAPI()
db_manager = DatabaseManager()
db_manager.init_db()
app.include_router(users_router.router, prefix="/api/v1", tags=["users"])
app.include_router(tasks_router.router, prefix="/api/v1", tags=["tasks"])


@app.get("/")
def root():
    return {"message": "Welcome to Barchasb Backend!"}
