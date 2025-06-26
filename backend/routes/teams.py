from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.pydantic_schemas import TeamCreate
from db.db_manager import get_db_session
from db.models import Team, User

router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create")
def create_team(team_data: TeamCreate, db_session: Session = Depends(get_db_session)):
    # TODO: CHECK JWT, for now lets assume check is always ok
    
    # Pull the required data from the request body
    team_name = team_data.name
    creator_id = team_data.creator_id

    # Find the user who want to create a team
    user = db_session.query(User).filter(User.id == creator_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such user")

    # Check if the user already has a team or team with same name exists
    existing_team = db_session.query(Team).filter((Team.creator_id == creator_id) | (Team.name == team_name)).first()
    if existing_team:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either the user already has created a team, or a team with same name exists")
    
    # TODO: Generate the invitation code for team
    CODE = "ABC123"

    new_team = Team(
        name=team_name,
        code=CODE,
        creator=user
    )
    db_session.add(new_team)
    db_session.commit()
    db_session.refresh(new_team)

    return {"message": "Team created successfully", "team_name": team_name, "creator_id": creator_id}