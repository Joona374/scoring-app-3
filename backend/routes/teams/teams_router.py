from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.pydantic_schema.player import PlayerResponse
from db.pydantic_schema.team import TeamCreate, TeamCreateResponse, TeamResponse
from db.db_manager import get_db_session
from db.models import Team, User, RegCode
from utils import get_current_user_id, generate_random_code, get_current_user_and_team

router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses={404: {"description": "Not found"}},
)


@router.post("/create")
def create_team(team_data: TeamCreate, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    # Find the user who wants to create a team (creator users may not have a team yet)
    user = db_session.query(User).filter(User.id == current_user_id).first()
    team = user.team if user else None

    # Pull the required data from the request body
    team_name = team_data.name.strip()

    # Check if the user already has a team or team with same name exists
    existing_team = db_session.query(Team).filter((Team.creator_id == user.id) | (Team.name == team_name)).first()
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

    team_created_response = TeamCreateResponse(team_name=new_team.name, code_for_team=new_team.code[0].code)

    return team_created_response


@router.get("/me")
def get_my_team(db_session: Session = Depends(get_db_session), user_and_team: tuple[User, Team] = Depends(get_current_user_and_team)):
    _, team = user_and_team

    if not team:
        return TeamResponse(
        team_name=None,
        join_code=None,
        players=None)

    teams_players = []
    if team.players:
        for player in team.players:
            player_response = PlayerResponse(
                id=player.id,
                first_name=player.first_name,
                last_name=player.last_name,
                jersey_number=player.jersey_number,
                position=player.position.name
                )
            teams_players.append(player_response)

    team_response = TeamResponse(
        team_name=team.name,
        join_code=team.code[0].code,
        players=teams_players)

    return team_response
