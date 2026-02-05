from collections import defaultdict
from io import BytesIO
from typing import TypedDict

from fastapi import Depends, APIRouter, Response
from openpyxl import load_workbook
from sqlalchemy.orm import Session, joinedload

from routes.excel.game_stats.get_stats import get_outcome_cell_adjustment
from db.db_manager import get_db_session
from db.models import ShotAreaTypes, PlayerStatsTag, ShotResultTypes, ShotTypeTypes, Team, User
from utils import get_current_user_and_team

class PlayerStats(TypedDict):
    games: int
    first_name: str
    last_name: str
    shooter_tags: list
    on_ice_tags: list
    cell_values: dict
    per_game_stats: list

router = APIRouter()

########################## FOR PLAYER SCORING  #####################
def collect_shooter_zones(player_stats_tags: list[PlayerStatsTag]) -> dict:
    ZONE_COLUMN_MAPPING = {
        ShotAreaTypes.ZONE_1: "B",
        ShotAreaTypes.ZONE_2_MIDDLE: "D",
        ShotAreaTypes.ZONE_2_SIDE: "F",
        ShotAreaTypes.HIGH_SLOT: "H",
        ShotAreaTypes.BLUELINE: "J",
        ShotAreaTypes.ZONE_4: "L",
        ShotAreaTypes.OUTSIDE_FAR: "N",
        ShotAreaTypes.OUTSIDE_CLOSE: "P",
        ShotAreaTypes.MISC: "R",
    }

    BASE_ROW = 4

    zone_cell_stats_dict = defaultdict(int)
    for tag in player_stats_tags:
        cell_col = ZONE_COLUMN_MAPPING[tag.shot_area.value]
        cell = f"{cell_col}{BASE_ROW}"
        zone_cell_stats_dict[cell] += 1

        # If its a goal
        if tag.shot_result.value == ShotResultTypes.GOAL_FOR:
            cell_col = chr(ord(ZONE_COLUMN_MAPPING[tag.shot_area.value]) + 1)
            zone_cell_stats_dict[f"{cell_col}{BASE_ROW}"] += 1

    return zone_cell_stats_dict


def collect_shooter_shot_types(player_stats_tags: list[PlayerStatsTag]) -> dict:
    TYPE_COLUMN_MAPPING = {
        ShotTypeTypes.CARRY_SHOT: "B",
        ShotTypeTypes.CAN_SHOT: "D",
        ShotTypeTypes.ONE_TIMER: "F",
        ShotTypeTypes.LOWHIGH_SHOT: "N",
        ShotTypeTypes.TAKEAWAY_SHOT: "P",
        ShotTypeTypes.REBOUND_SHOT: "R",
        ShotTypeTypes.DEFLECTION_SHOT: "T",
    }

    BASE_ROW = 11

    type_cell_stats_dict = defaultdict(int)
    for tag in player_stats_tags:
        cell_col = TYPE_COLUMN_MAPPING[tag.shot_type.value]
        cell = f"{cell_col}{BASE_ROW}"
        type_cell_stats_dict[cell] += 1

        # If its a goal
        if tag.shot_result.value == ShotResultTypes.GOAL_FOR:
            cell_col = chr(ord(TYPE_COLUMN_MAPPING[tag.shot_type.value]) + 1)
            type_cell_stats_dict[f"{cell_col}{BASE_ROW}"] += 1

    return type_cell_stats_dict


def collect_shooter_net_zones(player_stats_tags: list[PlayerStatsTag]) -> dict:
    WIDTH_COLUMN_MAPPING = {
        "Left": "G",
        "Mid": "H",
        "Right": "I",
    }

    HEIGHT_ROW_MAPPING = {
        "Top": 0,
        "Mid": 1,
        "Bottom": 2,
    }

    BASE_ROW = 17

    netzone_cell_stats_dict = defaultdict(int)
    for tag in player_stats_tags:
        cell_col = WIDTH_COLUMN_MAPPING[tag.net_width]
        cell_row = BASE_ROW + HEIGHT_ROW_MAPPING[tag.net_height]
        cell = f"{cell_col}{cell_row}"
        netzone_cell_stats_dict[cell] += 1

        if tag.shot_result.value == ShotResultTypes.GOAL_FOR:
            goal_col = chr(ord(cell_col) - 5)
            netzone_cell_stats_dict[f"{goal_col}{cell_row}"] += 1

    return netzone_cell_stats_dict


def collect_shooter_strengths(player_stats_tags: list[PlayerStatsTag]) -> dict:
    STRENGTHS_COLUMN_MAPPING = {
        "ES": "B",
        "PP": "C",
        "PK": "D",
        "EN+": "E",
        "EN-": "F",
    }

    BASE_ROW = 31
    strengths_cell_stats_dict = defaultdict(int)
    for tag in player_stats_tags:
        cell_col = STRENGTHS_COLUMN_MAPPING[tag.strengths]
        cell = f"{cell_col}{BASE_ROW}"
        strengths_cell_stats_dict[cell] += 1

        # If its a goal, also increment the corresponding chance
        if tag.shot_result.value == ShotResultTypes.GOAL_FOR:
            strengths_cell_stats_dict[f"{cell_col}{BASE_ROW + 1}"] += 1

    return strengths_cell_stats_dict


def find_players_on_ice_tags(player_stats_tags: list[PlayerStatsTag]) -> dict:
    """
    Aggregates a dictionary mapping each player ID to a list of PlayerStatsTag objects in which the player was on ice.
    Args:
        player_stats_tags (list[PlayerStatsTag]): A list of PlayerStatsTag objects, each containing information about players on ice.
    Returns:
        dict: A dictionary mapping each player ID to a list of PlayerStatsTag objects in which the player was on ice.
    """

    tags_for_each_player = defaultdict(list)

    for tag in player_stats_tags:
        for on_ice_tag in tag.players_on_ice:
            tags_for_each_player[on_ice_tag.player_id].append(tag)

    return tags_for_each_player


def collect_shooter_total_strengths(players_on_ice_tags: list[PlayerStatsTag], player_id: int) -> dict:
    STRENGTHS_COLUMN_MAPPING = {
        "ES": "B",
        "PP": "E",
        "PK": "H",
        "EN+": "K",
        "EN-": "N",
    }

    strengths_cell_stats_dict = defaultdict(int)
    for tag in players_on_ice_tags:
        participating_player_ids = [participating_tag.player_id for participating_tag in tag.players_participating]

        if player_id in participating_player_ids:
            base_rows = [38, 46]
        else:
            base_rows = [46]

        adjustment = get_outcome_cell_adjustment(tag)
        for row in base_rows:
            cell_col = chr(ord(STRENGTHS_COLUMN_MAPPING[tag.strengths]) + adjustment["column"])
            cell_row = row + adjustment["row"]
            cell = f"{cell_col}{cell_row}"
            strengths_cell_stats_dict[cell] += 1

            # If its a goal, also increment the corresponding chance
            if tag.shot_result.value in [ShotResultTypes.GOAL_FOR, ShotResultTypes.GOAL_AGAINST]:
                strengths_cell_stats_dict[f"{cell_col}{cell_row - 1}"] += 1

    return strengths_cell_stats_dict


def collect_players_per_game_stats(players_stats_tags: list[PlayerStatsTag], player_id: int) -> list[dict]:
    game_cell_values = {}
    for tag in players_stats_tags:
        if tag.strengths == "ES":
            chance_col_ord = 71
        elif tag.strengths == "PP":
            chance_col_ord = 84
        elif tag.strengths == "PK":
            chance_col_ord = 97
        elif tag.strengths in ["EN+", "EN-"]:
            continue
        else:
            raise ValueError(f"Unknown strengths value: {tag.strengths}")

        if tag.game_id not in game_cell_values:
            game_cell_values[tag.game_id] = {}
            game_cell_values[tag.game_id]["date"] = tag.game.date
            game_cell_values[tag.game_id]["A"] = f"{tag.game.date} vs {tag.game.opponent}"
            for col in ["C", "D", "G", "H", "J", "K", "M", "N", "P", "Q", "T", "U", "W", "X", "Z", "AA", "AC", "AD", "AG", "AH", "AJ", "AK", "AM", "AN", "AP", "AQ"]:
                game_cell_values[tag.game_id][col] = 0

        if tag.shooter_id == player_id:
            game_cell_values[tag.game_id]["D"] += 1
            if tag.shot_result.value == ShotResultTypes.GOAL_FOR:
                game_cell_values[tag.game_id]["C"] += 1

        if tag.shot_result.value == ShotResultTypes.GOAL_AGAINST:
            chance_col_ord += 1
        elif tag.shot_result.value == ShotResultTypes.CHANCE_FOR:
            chance_col_ord += 3
        elif tag.shot_result.value == ShotResultTypes.CHANCE_AGAINST:
            chance_col_ord += 4

        if chance_col_ord > 90:
            chance_col = f"A{chr(chance_col_ord-26)}"
        else:
            chance_col = chr(chance_col_ord)
        game_cell_values[tag.game_id][chance_col] += 1

        participating_player_ids = [participating_tag.player_id for participating_tag in tag.players_participating]
        if player_id in participating_player_ids:
            participating_col_ord = chance_col_ord + 6
            if participating_col_ord > 90:
                participating_col = f"A{chr(participating_col_ord-26)}"
            else:
                participating_col = chr(participating_col_ord)
            game_cell_values[tag.game_id][participating_col] += 1

    sorted_games = sorted(game_cell_values.values(), key=lambda d: d["date"], reverse=True)
    return sorted_games


@router.get("/player-stats")
async def get_player_scoring_excel(game_ids: str | None = None, db_session: Session = Depends(get_db_session), user_and_team: tuple["User", "Team"] = Depends(get_current_user_and_team)):
    _, team = user_and_team
    teams_games = team.games
    if game_ids:
        teams_games = []
        split_ids = [int(game_id) for game_id in game_ids.split(",")]
        for game in team.games:
            if game.id in split_ids:
                teams_games.append(game)
    selected_game_ids = [game.id for game in teams_games]

    player_stats_tags = (
        db_session.query(PlayerStatsTag)
        .options(
            joinedload(PlayerStatsTag.shooter),
            joinedload(PlayerStatsTag.game),
            joinedload(PlayerStatsTag.shot_result),
            joinedload(PlayerStatsTag.shot_area),
            joinedload(PlayerStatsTag.shot_type),
            joinedload(PlayerStatsTag.players_on_ice),
            joinedload(PlayerStatsTag.players_participating),
        )
        .filter(PlayerStatsTag.game_id.in_(selected_game_ids))
        .all()
    )

    players_to_analyze: defaultdict[int, PlayerStats] = defaultdict(lambda: {"games": 0, 
                                                                             "first_name": "", 
                                                                             "last_name": "", 
                                                                             "shooter_tags": [], 
                                                                             "on_ice_tags": [], 
                                                                             "cell_values": {}, 
                                                                             "per_game_stats": []}
                                                                             )
    for game in teams_games:

        for in_roster_object in game.in_rosters:
            player = in_roster_object.player
            if player.id not in players_to_analyze:
                players_to_analyze[player.id]["first_name"] = player.first_name
                players_to_analyze[player.id]["last_name"] = player.last_name

            players_to_analyze[player.id]["games"] += 1

    for tag in player_stats_tags:
        if tag.shooter:
            players_to_analyze[tag.shooter.id]["shooter_tags"].append(tag)

    on_ice_tags_for_each_player = find_players_on_ice_tags(player_stats_tags)  # {"player1_id": [PlayerStatsTags],..}
    for player_id, on_ice_tags in on_ice_tags_for_each_player.items():
        players_to_analyze[player_id]["on_ice_tags"] = on_ice_tags

    for player_id, player_data in players_to_analyze.items():
        zones = collect_shooter_zones(player_data["shooter_tags"])
        types = collect_shooter_shot_types(player_data["shooter_tags"])
        net_zones = collect_shooter_net_zones(player_data["shooter_tags"])
        strengths = collect_shooter_strengths(player_data["shooter_tags"])
        total_strengths = collect_shooter_total_strengths(player_data["on_ice_tags"], player_id)
        per_games_stats = collect_players_per_game_stats(player_data["on_ice_tags"], player_id)

        player_cell_values = {**zones, **types, **net_zones, **strengths, **total_strengths, "G1": player_data["games"]}
        players_to_analyze[player_id]["cell_values"] = player_cell_values
        players_to_analyze[player_id]["per_game_stats"] = per_games_stats

    # Load the excel file and template sheet
    workbook = load_workbook("excels/players_summary_template.xlsx")
    template_sheet = workbook.worksheets[0]

    for player_id, player_data in players_to_analyze.items():
        game_sheet = workbook.copy_worksheet(template_sheet)
        game_sheet.title = f"{player_data["last_name"].upper()} {player_data["first_name"]}"

        for cell, value in player_data["cell_values"].items():
            game_sheet[cell] = value

        for i, game in enumerate(player_data["per_game_stats"]):
            row = 54 + i
            for col, value in game.items():
                if col == "date":
                    continue
                cell = f"{col}{row}"
                game_sheet[cell] = value

    # Delete template sheet
    workbook.remove(workbook.worksheets[0])
    workbook.remove(workbook.worksheets[0])

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return Response(
        content=output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=pelaajayhteenveto.xlsx"}
    )


########################## FOR PLAYER SCORING  #####################
