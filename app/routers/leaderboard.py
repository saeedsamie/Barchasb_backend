from fastapi import APIRouter

router = APIRouter()

users_db = {}


@router.get("/")
def get_leaderboard():
    leaderboard_entries = [
        {"username": user.username, "points": user.points}
        for user in users_db.values()
    ]
    leaderboard_entries.sort(key=lambda x: x["points"], reverse=True)
    return leaderboard_entries
