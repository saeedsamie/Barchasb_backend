from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.DatabaseManager import DatabaseManager, PROD_DB_URL
from app.schemas.task import TaskCreate, TaskResponse
from app.schemas.taskReport import TaskReportCreate
from app.controller import (
    add_task,
    get_task_feed,
    report_task,
)

# Initialize the database manager
db_manager = DatabaseManager(PROD_DB_URL)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/new", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(db_manager.get_db)):
    try:
        created_task = add_task(
            db, type=task.type, data=task.data, point=task.point, tags=task.tags
        )
        return TaskResponse(status="success", task_id=created_task.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/feed", response_model=List[TaskCreate])
def fetch_task_feed(limit: int, db: Session = Depends(db_manager.get_db)):
    try:
        tasks = get_task_feed(db, limit=limit)
        return [
            TaskCreate(
                status="success",
                task_id=task.id,
                type=task.type,
                data=task.data,
                point=task.point,
                tags=task.tags,
            )
            for task in tasks
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# @router.put("/update/{task_id}/status", response_model=TaskResponse)
# def modify_task_status(task_id: str, new_status: str, db: Session = Depends(db_manager.get_db)):
#     try:
#         updated_task = update_task_status(db, task_id=task_id, new_status=new_status)
#         return TaskResponse(
#             status="success",
#             task_id=updated_task.id
#         )
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


@router.post("/report", response_model=dict)
def report_existing_task(report: TaskReportCreate, db: Session = Depends(db_manager.get_db)):
    try:
        # Validate the report and save
        report_result = report_task(db, report=report)
        return {"status": "success", "message": f"Task report successfully created {report_result.id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Report failed: {str(e)}")
