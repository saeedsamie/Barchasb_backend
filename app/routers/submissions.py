from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_submissions():
    return {"message": "List of submissions"}
