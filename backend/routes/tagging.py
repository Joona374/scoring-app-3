from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
import json
from db.pydantic_schemas import AddTag, TagSchema, GameInRosterResponse, PlayerResponse, TeamStatsTagResponse
from db.models import User, Game, ShotResult, ShotType, ShotResultTypes, ShotTypeTypes, TeamStatsTag, PlayerStatsTag, PlayerStatsTagOnIce, PlayerStatsTagParticipating
from db.db_manager import get_db_session
from sqlalchemy.orm import Session
from utils import get_current_user_id

router = APIRouter(
    prefix="/tagging",
    tags=["tagging"],
    responses={404: {"description": "Not found"}},
)

@router.get("/questions")
def get_questions():
    questions_json_path = Path("./tagging/player_stats_questions.json")
    text = questions_json_path.read_text()
    parsed_json = json.loads(text)

    return parsed_json

@router.post("/add-team-tag")
def add_game_stats_tag(tag_data: AddTag, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    filtered_tag = {k: v for k, v in tag_data.tag.items() if k != "new_question"}
    tag_for_model = {}
    for key, value in filtered_tag.items():
        key_to_use = key
        tag_for_model[key_to_use] = value


    print(tag_for_model)
    new_team_stats_tag = TeamStatsTag(**tag_for_model)
    db_session.add(new_team_stats_tag)
    db_session.commit()

    return TeamStatsTagResponse(id=new_team_stats_tag.id, succes=True, tag=filtered_tag)



@router.post("/add-players-tag")
def add_tag(tag_data: AddTag, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    received_tag = tag_data.tag
    print(received_tag)


    shot_location = received_tag["location"]
    if not ((0 <= shot_location["x"] <= 100) and (0 <= shot_location["y"] <= 100)):
        print(f"Invalid shot location: {shot_location}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad coordinates")

    shot_result_enum = ShotResultTypes.from_string(received_tag["shot_result"])
    shot_result_ref = db_session.query(ShotResult).filter(ShotResult.value == shot_result_enum).first()
    if not shot_result_ref:
        print(f"Invalid shot result: {received_tag['shot_result']}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad shot result")

    if received_tag["shot_type"]:
        shot_type_enum = ShotTypeTypes.from_string(received_tag["shot_type"])
        shot_type_ref = db_session.query(ShotType).filter(ShotType.value == shot_type_enum).first()
        if not shot_type_ref:
            print(f"Invalid shot type: {received_tag['shot_type']}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad shot type")
    else:
        shot_type_ref = None

    cross_ice = received_tag.get("crossice", None)
    if received_tag.get("shooter"):
        shooter_id = received_tag["shooter"]["id"]
    else:
        shooter_id = None

    print(received_tag["strengths"])

    try:
        new_tag = PlayerStatsTag(
            ice_x=shot_location["x"],
            ice_y=shot_location["y"],
            shot_result=shot_result_ref,
            shot_type=shot_type_ref,
            game_id=received_tag["game_id"],
            crossice=cross_ice,
            strengths=received_tag["strengths"],
            shooter_id=shooter_id
        )
        db_session.add(new_tag)
        db_session.flush()


        for on_ice_id in received_tag["on_ices"]:
            new_on_ice_tag = PlayerStatsTagOnIce(
                player_id=on_ice_id,
                tag_id=new_tag.id
            )
            db_session.add(new_on_ice_tag)

        for participant_id in received_tag["participations"]:
            new_participant_tag = PlayerStatsTagParticipating(
                player_id=participant_id,
                tag_id=new_tag.id
            )
            db_session.add(new_participant_tag)

        db_session.commit()

    except Exception as e:
        print(e)
        db_session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error recording the tag to db.")


    return {"success": True}


@router.get("/roster-for-game")
def get_roster_for_game(game_id: int, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    print(game_id)
    user = db_session.query(User).filter(User.id == current_user_id).first()
    game = db_session.query(Game).filter(Game.id == game_id).first()

    print(user.team)
    print("Is this same")
    print(game.team)

    if user.team != game.team:
        # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User has no rights to this game")
        print("Oh no")

    players_in_roster = []
    for in_roster in game.in_rosters:
        player_object = in_roster.player

        player_in_roster =  GameInRosterResponse(
            line=in_roster.line,
            position=in_roster.position,
            player=PlayerResponse(
                id=player_object.id,
                first_name=player_object.first_name,
                last_name=player_object.last_name,
                position=player_object.position
            )
        )
        players_in_roster.append(player_in_roster)

    return players_in_roster