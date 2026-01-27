from collections import defaultdict
from typing import Any, TypeAlias
from io import BytesIO
from enum import Enum

from openpyxl import Workbook, load_workbook
from sqlalchemy.orm import Session, joinedload
from fastapi import Depends, APIRouter, Response

from db.models import Game, User, Team, PlayerStatsTag, ShotResultTypes, ShotAreaTypes, ShotTypeTypes
from db.db_manager import get_db_session
from utils import get_current_user_and_team

TOTAL_STATS_CELL_VALUES = "cell_values"
TOTAL_STATS_MAP_COORDINATES = "coordinates"
MAPPED_DATA_FOR = "for"
MAPPED_DATA_AGAINST = "against"


class MapCategories(str, Enum):
    ICE = "ice"
    NET = "net"


Point: TypeAlias = tuple[int, int]
CategoryMap: TypeAlias = defaultdict[MapCategories, list[Point]]
ResultMap: TypeAlias = dict[ShotResultTypes, CategoryMap]

MAP_RESULT_MAPPING: dict[ShotResultTypes, list[ShotResultTypes]] = {
    ShotResultTypes.CHANCE_FOR: [ShotResultTypes.CHANCE_FOR],
    ShotResultTypes.GOAL_FOR: [ShotResultTypes.CHANCE_FOR, ShotResultTypes.GOAL_FOR],
    ShotResultTypes.CHANCE_AGAINST: [ShotResultTypes.CHANCE_AGAINST],
    ShotResultTypes.GOAL_AGAINST: [ShotResultTypes.CHANCE_AGAINST, ShotResultTypes.GOAL_AGAINST],
}

router = APIRouter() 

########################## FOR GAME STATS  #######################
def get_outcome_cell_adjustment(tag: PlayerStatsTag) -> dict:
    """
    Calculates the adjustment to be made to a cell's row and column based on the outcome of a player's shot.
    Args:
        tag (PlayerStatsTag): An object containing information about the player's shot, including its result type.
    Returns:
        dict: A dictionary with 'row' and 'column' keys indicating the adjustment values to be applied.
    The adjustment is determined as follows:
        - If the shot result is CHANCE_AGAINST: column is incremented by 1.
        - If the shot result is GOAL_FOR: row is incremented by 1.
        - If the shot result is GOAL_AGAINST: both row and column are incremented by 1.
        - For CHANCE_FOR: no adjustment is made (row and column remain 0).
    """

    adjustment = {"row": 0, "column": 0}

    result_type = tag.shot_result.value

    if result_type == ShotResultTypes.CHANCE_AGAINST:
        adjustment["column"] = 1
    elif result_type == ShotResultTypes.GOAL_FOR:
        adjustment["row"] = 1
    elif result_type == ShotResultTypes.GOAL_AGAINST:
        adjustment["column"] = 1
        adjustment["row"] = 1

    return adjustment


def collect_shotzone_data(player_stats_tags: list[PlayerStatsTag]) -> dict:
    """
    Collects and aggregates shot zone data from a list of PlayerStatsTag objects.
    This function maps each shot area type to a specific Excel column, applies any necessary cell adjustments
    based on the outcome, and counts the occurrences of each resulting cell. The result is a dictionary
    mapping Excel cell references (e.g., "B5", "D6") to the number of times shots occurred in those zones.
    Args:
        player_stats_tags (list[PlayerStatsTag]): A list of PlayerStatsTag objects representing shot events.
    Returns:
        dict: A dictionary where keys are Excel cell references (str) and values are the counts (int) of shots in those cells.
    """

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

    BASE_ROW = 5

    zone_cell_stats_dict = defaultdict(int)
    for tag in player_stats_tags:
        adjustment = get_outcome_cell_adjustment(tag)
        cell_col = chr(ord(ZONE_COLUMN_MAPPING[tag.shot_area.value]) + adjustment["column"])
        cell_row = BASE_ROW + adjustment["row"]
        cell = f"{cell_col}{cell_row}"
        zone_cell_stats_dict[cell] += 1

        # If its a goal, also increment the corresponding chance
        if cell_row == 6:
            zone_cell_stats_dict[f"{cell_col}{cell_row - 1}"] += 1

    return zone_cell_stats_dict


def collect_shot_type_data(player_stats_tags: list[PlayerStatsTag]) -> dict:
    """
    Collects and aggregates shot type data from a list of PlayerStatsTag objects, mapping each shot type to a specific Excel cell.
    Args:
        player_stats_tags (list[PlayerStatsTag]): A list of PlayerStatsTag objects representing individual shot events.
    Returns:
        dict: A dictionary where keys are Excel cell references (e.g., "B12") and values are the counts of shots mapped to those cells.
    Notes:
        - The mapping of shot types to Excel columns is defined in TYPE_COLUMN_MAPPING.
        - The row is determined by BASE_ROW and may be adjusted based on the outcome and whether the shot was cross-ice.
        - The function uses get_outcome_cell_adjustment to determine cell adjustments.
    """

    TYPE_COLUMN_MAPPING = {
        ShotTypeTypes.CARRY_SHOT: "B",
        ShotTypeTypes.CAN_SHOT: "D",
        ShotTypeTypes.ONE_TIMER: "F",
        ShotTypeTypes.LOWHIGH_SHOT: "N",
        ShotTypeTypes.TAKEAWAY_SHOT: "P",
        ShotTypeTypes.REBOUND_SHOT: "R",
        ShotTypeTypes.DEFLECTION_SHOT: "T",
    }

    BASE_ROW = 12
    type_cell_stats_dict = defaultdict(int)
    for tag in player_stats_tags:
        adjustment = get_outcome_cell_adjustment(tag)
        if tag.crossice:
            adjustment["column"] += 6
        cell_col = chr(ord(TYPE_COLUMN_MAPPING[tag.shot_type.value]) + adjustment["column"])
        cell_row = BASE_ROW + adjustment["row"]
        cell = f"{cell_col}{cell_row}"
        type_cell_stats_dict[cell] += 1

        # If its a goal, also increment the corresponding chance
        if cell_row == 13:
            type_cell_stats_dict[f"{cell_col}{cell_row - 1}"] += 1

    return type_cell_stats_dict


def collect_net_zone_data(player_stats_tags: list[PlayerStatsTag]) -> dict:
    WIDTH_COLUMN_MAPPING = {
        "Left": "C",
        "Mid": "D",
        "Right": "E",
    }

    HEIGHT_ROW_MAPPING = {
        "Top": 0,
        "Mid": 1,
        "Bottom": 2,
    }

    def get_adjustment(tag):
        adjustment = {"row": 0, "column": 0}
        result_type = tag.shot_result.value

        if result_type == ShotResultTypes.CHANCE_FOR:
            adjustment["column"] = 5
        elif result_type == ShotResultTypes.GOAL_AGAINST:
            adjustment["row"] = 7
        elif result_type == ShotResultTypes.CHANCE_AGAINST:
            adjustment["column"] = 5
            adjustment["row"] = 7

        return adjustment

    BASE_ROW = 19

    netzone_cell_stats_dict = defaultdict(int)
    for tag in player_stats_tags:
        adjustment = get_adjustment(tag)
        cell_col = chr(ord(WIDTH_COLUMN_MAPPING[tag.net_width]) + adjustment["column"])
        cell_row = BASE_ROW + HEIGHT_ROW_MAPPING[tag.net_height] + adjustment["row"]
        cell = f"{cell_col}{cell_row}"
        netzone_cell_stats_dict[cell] += 1

        if cell_col in ["C", "D", "E"]:
            chance_col = chr(ord(cell_col) + 5)
            netzone_cell_stats_dict[f"{chance_col}{cell_row}"] += 1

    return netzone_cell_stats_dict


def collect_shot_strengths_data(player_stats_tags: list[PlayerStatsTag]) -> dict:
    """
    Collects and aggregates shot strengths data from a list of PlayerStatsTag objects.
    This function maps each the number of players on the ice to a specific Excel cell based on predefined
    column mappings and calculated row/column adjustments. It then counts the occurrences of each
    cell reference, effectively summarizing the shot strengths distribution for later use in Excel export.
    Args:
        player_stats_tags (list[PlayerStatsTag]): A list of PlayerStatsTag objects containing shot strength information.
    Returns:
        dict: A dictionary where keys are Excel cell references (e.g., "B35") and values are the counts
              of shots mapped to each cell.
    """

    STRENGTHS_COLUMN_MAPPING = {
        "ES": "B",
        "PP": "D",
        "PK": "F",
        "EN+": "H",
        "EN-": "J",
    }

    BASE_ROW = 35
    strengths_cell_stats_dict = defaultdict(int)
    for tag in player_stats_tags:
        adjustment = get_outcome_cell_adjustment(tag)
        cell_col = chr(ord(STRENGTHS_COLUMN_MAPPING[tag.strengths]) + adjustment["column"])
        cell_row = BASE_ROW + adjustment["row"]
        cell = f"{cell_col}{cell_row}"
        strengths_cell_stats_dict[cell] += 1

        # If its a goal, also increment the corresponding chance
        if cell_row == 36:
            strengths_cell_stats_dict[f"{cell_col}{cell_row - 1}"] += 1

    return strengths_cell_stats_dict


def collect_mapped_data(scoring_chances: list[PlayerStatsTag]) -> ResultMap:
    """
    Collects and maps scoring chance data into a structured format.

    Args:
        scoring_chances (list[PlayerStatsTag]): List of scoring chances to process.

    Returns:
        ResultMap: Dictionary mapping shot results to categories with ice and net coordinates.
            So data[ShotResultTypes][MapCategories] is a list of (int, int)
                    What outcome? Net or ice image? List of coordinates to draw.
    """

    data: ResultMap = {result: defaultdict(list) for result in ShotResultTypes}
    for chance in scoring_chances:
        ice = (chance.ice_x, chance.ice_y)
        net = (chance.net_x, chance.net_y)

        for result in MAP_RESULT_MAPPING[chance.shot_result.value]:
            data[result][MapCategories.ICE].append(ice)
            data[result][MapCategories.NET].append(net)

    return data


def build_total_stats(scoring_chances: list[PlayerStatsTag]) -> dict[str, dict[str, int]]:
    """
    Builds total game statistics by aggregating shot zone, shot type, net zone, strengths, and mapped data from scoring chances.
    Args:
        scoring_chances (list[PlayerStatsTag]): List of player statistics tags.
    Returns:
        dict[str, dict[str, int]]: Dictionary containing total stats with cell values and map coordinates.
    """

    shot_zone_data = collect_shotzone_data(scoring_chances)
    shot_type_data = collect_shot_type_data(scoring_chances)
    net_zone_data = collect_net_zone_data(scoring_chances)
    strengths_data = collect_shot_strengths_data(scoring_chances)

    mapped_data = collect_mapped_data(scoring_chances)

    total_stats = {TOTAL_STATS_CELL_VALUES: {**shot_zone_data, **shot_type_data, **net_zone_data, **strengths_data}, TOTAL_STATS_MAP_COORDINATES: mapped_data}

    return total_stats


def get_scoring_games_data(teams_games: list[Game], db_session: Session) -> tuple[list[dict[str, Any]], dict[str, dict[str, int]]]:
    """
    Collects and aggregates scoring-related statistics for a list of games.
    For each game in the provided list, this function gathers various player statistics
    (such as shot zones, shot types, net zones, and shot strengths) from the database,
    aggregates them per game, and also computes the totals across all games.
    Args:
        teams_games (list[Game]): A list of Game objects for which to collect statistics.
        db_session (Session): An active SQLAlchemy database session.
    Returns:
        tuple:
            - per_game_stats (list[dict]): A list of dictionaries, each containing:
                - "date": The date of the game.
                - "opponent": The opponent team.
                - "home": Boolean indicating if the game was at home.
                - "cell_values": A dictionary with aggregated statistics for the game.
            - total_stats (dict): A dictionary with aggregated statistics across all games.
                - "cell_values": dict where keys are excel cell names and values are int value to write on the cell
    """

    game_ids = [game.id for game in teams_games]

    player_stats_tags = (
        db_session.query(PlayerStatsTag)
        .options(
            joinedload(PlayerStatsTag.shot_result),
            joinedload(PlayerStatsTag.shot_area),
            joinedload(PlayerStatsTag.shot_type),
        )
        .filter(PlayerStatsTag.game_id.in_(game_ids))
        .all()
    )

    total_stats = build_total_stats(player_stats_tags)

    # TODO:
    # 1. Abstract the code below in to a helper
    # (build_per_game_stats) similar to build_total_stats
    #
    # 2. After getting the map (net and ice image) data (coordinates)
    # to the dicts returned here, go to create_game_stats_workbook.
    # Abstract the per game sheet writing to a helper.
    #
    # 3. Add methods that take the template images,
    # Take the map coordinates and draw those to game and total sheets
    # And attaches them to the sheets
    game_tags = defaultdict(list)
    for tag in player_stats_tags:
        game_tags[tag.game_id].append(tag)

    per_game_stats = []
    for game in teams_games:
        game_data = {}
        game_data["date"] = game.date
        game_data["opponent"] = game.opponent
        game_data["home"] = game.home

        tags_for_game = game_tags[game.id]
        shot_zone_data = collect_shotzone_data(tags_for_game)
        shot_type_data = collect_shot_type_data(tags_for_game)
        net_zone_data = collect_net_zone_data(tags_for_game)
        strengths_data = collect_shot_strengths_data(tags_for_game)

        game_cell_values = {**shot_zone_data, **shot_type_data, **net_zone_data, **strengths_data}
        game_data["cell_values"] = game_cell_values
        per_game_stats.append(game_data)

    return per_game_stats, total_stats


def get_filtered_team_games(team: Team, game_id_str: str | None) -> list["Game"]:
    if not game_id_str:
        return team.games

    else:
        split_ids = [int(game_id) for game_id in game_id_str.split(",")]
        teams_games = [game for game in team.games if game.id in split_ids]
        return teams_games


def write_total_sheet_for_game_stats(workbook: Workbook, total_cell_values: dict[str, int]):
    total_sheet = workbook.worksheets[1]

    for cell, value in total_cell_values.items():
        total_sheet[cell] = value


def create_game_stats_workbook(total_stats: dict[str, dict[str, int]], per_game_stats: list[dict[str, Any]]) -> Workbook:
    workbook = load_workbook("excels/game_stats_template.xlsx")
    template_sheet = workbook.worksheets[0]

    write_total_sheet_for_game_stats(workbook, total_stats["cell_values"])

    # TODO: abstract this to helper similar to write_total_sheet_for_game_stats
    per_game_stats.sort(key=lambda game: game["date"], reverse=True)
    for game in per_game_stats:
        game_sheet = workbook.copy_worksheet(template_sheet)

        if "/" in game["opponent"]:
            sanitized_opponent = game["opponent"].replace("/", "&")
            game_sheet.title = f"{sanitized_opponent} {game['date']}"
        else:
            game_sheet.title = f"{game['opponent']} {game['date']}"

        game_sheet["C1"] = game["date"]
        game_sheet["G1"] = game["opponent"]
        game_sheet["T1"] = game["home"]

        for cell, value in game["cell_values"].items():
            game_sheet[cell] = value

    # Delete template sheet
    workbook.remove(workbook.worksheets[0])

    return workbook


@router.get("/game-stats")
async def get_team_scoring_excel(game_ids: str | None = None, db_session: Session = Depends(get_db_session), user_and_team: tuple["User", "Team"] = Depends(get_current_user_and_team)):
    _, team = user_and_team

    teams_games = get_filtered_team_games(team, game_ids)

    per_game_stats, total_stats = get_scoring_games_data(teams_games, db_session)

    workbook = create_game_stats_workbook(total_stats, per_game_stats)

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return Response(
        content=output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=pelitilastot.xlsx"}
    )

########################## FOR GAME STATS  #######################
