from typing import List

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.DatabaseManager import DatabaseManager
from app.controller.taskLabel_controller import submit_label
from app.controller.taskReport_controller import report_task
from app.controller.task_controller import add_task, get_task_feed
from app.routers.users_router import get_current_user
from app.schemas.task import TaskCreate, TaskResponse
from app.schemas.taskLabel import LabelCreate
from app.schemas.taskReport import TaskReport

# Initialize the database manager
db_manager = DatabaseManager()

router = APIRouter(prefix="/tasks", tags=["tasks"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


@router.post("/new", response_model=TaskResponse, status_code=201)
# todo Needs different type of authority
async def create_task(task: TaskCreate, db: Session = Depends(db_manager.get_db)):
    try:
        created_task = add_task(
            db, type=task.type, data=task.data, point=task.point, tags=task.tags, is_done=task.is_done
        )
        return TaskResponse(status="success", task_id=created_task.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/feed", response_model=List[TaskCreate])
async def fetch_task_feed(limit: int = Query(..., gt=0), current_user=Depends(get_current_user),
                         db: Session = Depends(db_manager.get_db)):
    """
    Get task feed with pagination.
    
    Args:
        limit: Number of tasks to return (must be greater than 0)
    """
    try:
        tasks = get_task_feed(current_user.id, db)
        return [TaskCreate(
            status="success",
            task_id=task.id,
            type=task.type,
            data=task.data,
            point=task.point,
            tags=task.tags,
        ) for task in tasks][-limit:]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/submit", response_model=dict)
async def submit_existing_task(label: LabelCreate, current_user=Depends(get_current_user),
                             db: Session = Depends(db_manager.get_db)):
    try:
        # First check authorization before any database operations
        if label.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to submit for another user"
            )

        submission_result = submit_label(
            db,
            task_id=label.task_id,
            user_id=label.user_id,
            content=str(label.content)
        )

        if not submission_result:
            raise HTTPException(
                status_code=400,
                detail="Failed to submit label"
            )

        return {
            "status": "success",
            "message": f"Task successfully submitted {submission_result.id}"
        }
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Submission failed: {str(e)}"
        )


@router.post("/report", response_model=dict)
async def report_existing_task(task_report: TaskReport, current_user=Depends(get_current_user),
                               db: Session = Depends(db_manager.get_db)):
    try:
        # Validate the report and save
        report_result = report_task(db, task_id=task_report.task_id, user_id=task_report.user_id,
                                    details=task_report.detail)
        return {"status": "success", "message": f"Task report successfully created {report_result.id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Report failed: {str(e)}")

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
