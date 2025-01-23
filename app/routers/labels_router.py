from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.controller.taskLabel_controller import submit_task
from app.schemas.taskLabel import LabelCreate

router = APIRouter()


@router.post("/submit", response_model=dict)
def submit_existing_task(label: LabelCreate, db: Session = Depends(db_manager.get_db)):
    try:
        # Ensure user_id and task_id exist before committing
        submission_result = submit_task(db, label=label)
        return {"status": "success", "message": f"Task successfully submitted {submission_result.id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Submission failed: {str(e)}")
