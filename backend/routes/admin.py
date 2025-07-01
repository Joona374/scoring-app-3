from fastapi import APIRouter
from db.create_tables import main as wipe_db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

@router.post("/clean-db")
def clean_db():
    try:
        creator_code = wipe_db()
        return {"Message": "Wiped db!", "creator_code": creator_code}
    except Exception as e:
        return {"Message": "DB WIPING FAILED", "ERROR": e}
