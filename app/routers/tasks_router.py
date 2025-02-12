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
from app.schemas.taskReport import CreateTaskReport

# Initialize the database manager
db_manager = DatabaseManager()

router = APIRouter(prefix="/tasks", tags=["tasks"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


@router.post("/new", response_model=TaskResponse, status_code=201)
async def create_task(task: TaskCreate, db: Session = Depends(db_manager.get_db)):
    """
    Create a new task in the system.

    Args:
        task (TaskCreate): Task creation data including type, data, points, title, description and tags
        db (Session): Database session dependency

    Returns:
        TaskResponse: Response containing task ID and status

    Raises:
        HTTPException: If task creation fails
    """
    try:
        created_task = add_task(
            db,
            type=task.type,
            data=task.data,
            point=task.point,
            title=task.title,
            description=task.description,
            tags=task.tags,
            is_done=task.is_done
        )
        return TaskResponse(status="success", task_id=created_task.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/feed", response_model=List[TaskCreate])
async def fetch_task_feed(limit: int = Query(..., gt=0), current_user=Depends(get_current_user),
                          db: Session = Depends(db_manager.get_db)):
    """
    Get a paginated feed of available tasks for the current user.
    
    Args:
        limit (int): Maximum number of tasks to return
        current_user (User): Current authenticated user
        db (Session): Database session dependency

    Returns:
        List[TaskCreate]: List of available tasks

    Raises:
        HTTPException: If fetching tasks fails
    """
    try:
        tasks = get_task_feed(current_user.id, db)
        return [TaskCreate(
            status="success",
            task_id=task.id,
            type=task.type,
            data=task.data,
            point=task.point,
            title=task.title,
            description=task.description,
            tags=task.tags,
        ) for task in tasks][-limit:]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/submit", response_model=dict)
async def submit_existing_task(label: LabelCreate, current_user=Depends(get_current_user),
                               db: Session = Depends(db_manager.get_db)):
    """
    Submit a label for an existing task.

    Args:
        label (LabelCreate): Label data including task_id and content
        current_user (User): Current authenticated user
        db (Session): Database session dependency

    Returns:
        dict: Success message with submission ID

    Raises:
        HTTPException: If submission fails or user is not authorized
    """
    try:
        submission_result = submit_label(
            db,
            task_id=label.task_id,
            user_id=current_user.id,
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
async def report_existing_task(task_report: CreateTaskReport, current_user=Depends(get_current_user),
                               db: Session = Depends(db_manager.get_db)):
    """
    Report an issue with an existing task.

    Args:
        task_report (CreateTaskReport): Report data including task_id and details
        current_user (User): Current authenticated user
        db (Session): Database session dependency

    Returns:
        dict: Success message with report ID

    Raises:
        HTTPException: If report submission fails
    """
    try:
        report_result = report_task(db, task_id=task_report.task_id, user_id=current_user.id,
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
