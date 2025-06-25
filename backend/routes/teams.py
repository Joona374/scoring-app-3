from fastapi import APIRouter, Depends
from db.pydantic_schemas import TeamCreate
from db.db_manager import get_db_session

router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create")
def create_team(team_data: TeamCreate, db_session = Depends(get_db_session)):
    print("Received team data:", team_data)

    # TODO: DO THIS LOGIC AND CREATE FRONTEND FORM FOR THIS

    # Return mock data for now
    return {"message": "User created successfully", "id": 69}