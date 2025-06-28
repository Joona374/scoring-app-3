from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import random
import string

from db.pydantic_schemas import TeamCreate
from db.db_manager import get_db_session
from db.models import Team, User, RegCode
from utils import get_current_user_id

router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses={404: {"description": "Not found"}},
)

def generate_random_code() -> str:
    random_code = ""
    for _ in range(6):
        random_code += random.choice(string.ascii_uppercase + string.digits + string.digits)
    return random_code

@router.post("/create")
def create_team(team_data: TeamCreate, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    # Pull the required data from the request body
    team_name = team_data.name
    
    # Find the user who want to create a team
    user = db_session.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such user")

    # Check if the user already has a team or team with same name exists
    existing_team = db_session.query(Team).filter((Team.creator_id == current_user_id) | (Team.name == team_name)).first()
    if existing_team:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either the user already has created a team, or a team with same name exists")
    
    code_for_team = generate_random_code()
    new_code = RegCode(
        code=code_for_team,
        creation_code=False,
        join_code=True
    )

    db_session.add(new_code)
    db_session.commit()


    new_team = Team(
        name=team_name,
        code=[new_code],
        creator=user
    )

    db_session.add(new_team)
    db_session.commit()

    new_code.team_related = new_team

    user.has_creation_privilege = False
    user.team = new_team
    
    db_session.commit()
    db_session.refresh(new_team)

    return {"message": "Team created successfully", "team_name": team_name, "creator_id": current_user_id, "code_for_team": new_code.code}