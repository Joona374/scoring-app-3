from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
import json
from db.pydantic_schemas import AddTag, TagSchema, GameInRosterResponse, PlayerResponse, TeamStatsTagResponse, PlayerStatsTagResponse
from db.models import User, Game, ShotResult, ShotType, ShotResultTypes, ShotTypeTypes, TeamStatsTag, PlayerStatsTag, PlayerStatsTagOnIce, PlayerStatsTagParticipating, ShotArea, ShotAreaTypes, GameInRoster
from db.db_manager import get_db_session
from sqlalchemy.orm import Session
from utils import get_current_user_id

router = APIRouter(
    prefix="/tagging",
    tags=["tagging"],
    responses={404: {"description": "Not found"}},
)

@router.get("/questions/team")
def get_questions():
    questions_json_path = Path("./tagging/team_stats_questions.json")
    text = questions_json_path.read_text()
    parsed_json = json.loads(text)

    return parsed_json

@router.get("/questions/player")
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

    new_team_stats_tag = TeamStatsTag(**tag_for_model)
    db_session.add(new_team_stats_tag)
    db_session.commit()

    return TeamStatsTagResponse(id=new_team_stats_tag.id, succes=True, tag=filtered_tag)



@router.post("/add-players-tag")
def add_tag(tag_data: AddTag, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    received_tag = tag_data.tag
    print(received_tag)


    shot_location = received_tag["location"]
    shot_zone = received_tag["shotZone"]
    net_location = received_tag["net"]

    shot_height, shot_width = received_tag["netZone"].split("-")

    if not ((0 <= shot_location["x"] <= 100) and (0 <= shot_location["y"] <= 100)):
        print(f"Invalid shot location: {shot_location}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad coordinates")

    shot_result_enum = ShotResultTypes.from_string(received_tag["shot_result"])
    shot_result_ref = db_session.query(ShotResult).filter(ShotResult.value == shot_result_enum).first()
    if not shot_result_ref:
        print(f"Invalid shot result: {shot_result_enum}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad shot result")

    shot_area_enum = ShotAreaTypes.from_string(shot_zone)
    shot_area_ref = db_session.query(ShotArea).filter(ShotArea.value == shot_area_enum).first()
    if not shot_area_ref:
        print(f"Invalid shot area: {shot_area_enum}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad shot area")

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


    try:
        new_tag = PlayerStatsTag(
            shot_result=shot_result_ref,
            ice_x=shot_location["x"],
            ice_y=shot_location["y"],
            shot_area=shot_area_ref,
            net_x = net_location["x"],
            net_y = net_location["y"],
            net_height=shot_height,
            net_width=shot_width,
            shot_type=shot_type_ref,
            game_id=received_tag["game_id"],
            crossice=cross_ice,
            strengths=received_tag["strengths"],
            shooter_id=shooter_id,

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


    return PlayerStatsTagResponse(id=new_tag.id, succes=True)

@router.get("/load/team-tags/{game_id}")
def load_team_tags(game_id: int, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    user = db_session.query(User).filter(User.id == current_user_id).first()
    game = db_session.query(Game).filter(Game.id == game_id).first()
    if user.team == game.team:
        tags = game.team_stats_tags
        return tags
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No permission to access these tags")


@router.get("/load/player-tags/{game_id}")
def load_player_tags(game_id: int, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    user = db_session.query(User).filter(User.id == current_user_id).first()
    game = db_session.query(Game).filter(Game.id == game_id).first()
    if user.team == game.team:
        tags = game.player_stats_tags
        normalized_tags = []
        for tag in tags:
            normal_tag = {
                "crossice": tag.crossice,
                "game_id": tag.game_id,
                "location": {"x": tag.ice_x, "y": tag.ice_y},
                "net": {"x": tag.net_x, "y": tag.net_y},
                "netZone": f"{tag.net_height}-{tag.net_width}",
                "shotZone": tag.shot_area.value, 
                "shot_result": tag.shot_result.value,
                "shot_type": tag.shot_type.value,
                "strengths": tag.strengths,
                "id": tag.id
            }
            if tag.shooter:
                normal_tag["shooter"] = {"id": tag.shooter.id, "first_name": tag.shooter.first_name, "last_name": tag.shooter.last_name, "jersey_number": tag.shooter.jersey_number, "position": tag.shooter.position}

            normalized_tags.append(normal_tag)
        return normalized_tags
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No permission to access these tags")

def create_position_response(line_n: int, position: str, in_rosters_list: list[GameInRoster]):
    in_roster_object = next((in_roster for in_roster in in_rosters_list if in_roster.line == line_n and in_roster.position == position), None)
    if in_roster_object:
        player_object = in_roster_object.player
        player_in_roster = GameInRosterResponse(
            line=in_roster_object.line,
            position=in_roster_object.position,
            player=PlayerResponse(
                id=player_object.id,
                first_name=player_object.first_name,
                last_name=player_object.last_name,
                jersey_number=player_object.jersey_number,
                position=player_object.position
            )
        )
    else:
        player_in_roster = GameInRosterResponse(
            line=line_n,
            position=position,
            player=None
        )

    return player_in_roster

@router.get("/roster-for-game")
def get_roster_for_game(game_id: int, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    user = db_session.query(User).filter(User.id == current_user_id).first()
    game = db_session.query(Game).filter(Game.id == game_id).first()

    if user.team != game.team:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User has no rights to this game")

    NUMBER_OF_FORWARD_LINES = 5
    NUMBER_OF_DEFENSE_LINES = 4
    NUMBER_OF_GOALIES = 2

    players_in_roster = []
    
    for i in range(1, NUMBER_OF_FORWARD_LINES + 1):
        for pos in ["LW", "C", "RW"]:
            player_in_roster = create_position_response(i, pos, game.in_rosters)
            players_in_roster.append(player_in_roster)

    for i in range(1, NUMBER_OF_DEFENSE_LINES + 1):
        for pos in ["LD", "RD"]:
            player_in_roster = create_position_response(i, pos, game.in_rosters)
            players_in_roster.append(player_in_roster)

    for i in range(1, NUMBER_OF_GOALIES + 1):
        player_in_roster = create_position_response(i, "G", game.in_rosters)
        players_in_roster.append(player_in_roster)

    return players_in_roster

def filter_changed_in_rosters(frontend_entries: list[GameInRosterResponse], db_entries: list[GameInRoster], game_id: int):
    matched = []
    for fe_entry in frontend_entries:
        match = find_in_roster_entry(fe_entry.line, fe_entry.position, db_entries)
        matched.append((fe_entry, match))

    rows_to_add = []
    rows_to_delete = []
    rows_to_update = []
    for pair in matched:
        fe_entry = pair[0]
        db_entry = pair[1]

        if fe_entry.player == None and db_entry == None:
            continue

        elif fe_entry.player != None and db_entry == None:
            new_db_entry = GameInRoster(
                game_id=game_id,
                line=fe_entry.line,
                position=fe_entry.position,
                player_id=fe_entry.player.id
            )
            rows_to_add.append(new_db_entry)

        elif fe_entry.player == None and db_entry != None:
            rows_to_delete.append(db_entry)

        elif fe_entry.player.id != db_entry.player_id:
            db_entry.player_id = fe_entry.player.id
            rows_to_update.append(db_entry)


    return rows_to_add, rows_to_delete, rows_to_update

def find_in_roster_entry(line: int, position: str, in_rosters: list[GameInRoster]):
    return next((entry for entry in in_rosters if entry.line == line and entry.position == position), None)

@router.put("/roster-for-game")
def update_roster_for_game(game_id: int, new_roster: list[GameInRosterResponse], db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    try:
        user = db_session.query(User).filter(User.id == current_user_id).first()
        game = db_session.query(Game).filter(Game.id == game_id).first()

        if user.team != game.team:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No permission to update this game's roster")

        roster_entries_for_game = db_session.query(GameInRoster).filter(GameInRoster.game_id == game_id).all()
        rows_to_add, rows_to_delete, rows_to_update = filter_changed_in_rosters(new_roster, roster_entries_for_game, game_id)

        for row in rows_to_add:
            db_session.add(row)

        for row in rows_to_delete:
            db_session.delete(row)

        for row in rows_to_update:
            pass
            # Do nothing change they were already changed inside filter_changed_in_roster()

        db_session.commit()
        return {"message": "Roster updated successfully", "success": True}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing the roster update")

@router.delete("/delete/team-tag/{tag_id}")
def update_player(tag_id: int, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    user = db_session.query(User).filter(User.id == current_user_id).first()
    tag = db_session.query(TeamStatsTag).filter(TeamStatsTag.id == tag_id).first()
    tag_game = tag.game

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if user.team != tag_game.team:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No permission to delete this tag")

    db_session.delete(tag)
    db_session.commit()

    return {"message": "Tag deleted successfully", "success": True}

@router.delete("/delete/player-tag/{tag_id}")
def update_player(tag_id: int, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    user = db_session.query(User).filter(User.id == current_user_id).first()
    tag = db_session.query(PlayerStatsTag).filter(PlayerStatsTag.id == tag_id).first()
    tag_game = tag.game

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if user.team != tag_game.team:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No permission to delete this tag")

    # TODO DELETING TAG SHOULD CASCADE TO DELETE Other stuff also
    db_session.delete(tag)
    db_session.commit()

    return {"message": "Tag deleted successfully", "success": True}