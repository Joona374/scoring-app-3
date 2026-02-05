from typing import Any
from collections import defaultdict
from sqlalchemy.orm import Session, joinedload
from routes.excel.excel_utils import get_outcome_cell_adjustment
from db.models import Game, PlayerStatsTag, ShotAreaTypes, ShotResultTypes, ShotTypeTypes
from routes.excel.game_stats.game_stats_utils import MAP_RESULT_MAPPING, MapCategories, ResultMap


STATS_CELL_VALUES = "cell_values"
STATS_MAP_COORDINATES = "coordinates"
MAPPED_DATA_FOR = "for"
MAPPED_DATA_AGAINST = "against"


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

    total_stats = {STATS_CELL_VALUES: {**shot_zone_data, **shot_type_data, **net_zone_data, **strengths_data}, STATS_MAP_COORDINATES: mapped_data}

    return total_stats


def build_per_game_stats(player_stats_tags: list[PlayerStatsTag], teams_games: list[Game]) -> list:
    game_tags = defaultdict(list[PlayerStatsTag])
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

        mapped_data = collect_mapped_data(tags_for_game)

        game_data[STATS_CELL_VALUES] = {**shot_zone_data, **shot_type_data, **net_zone_data, **strengths_data}
        game_data[STATS_MAP_COORDINATES] = mapped_data
        per_game_stats.append(game_data)

    return per_game_stats


def get_game_stats(teams_games: list[Game], db_session: Session) -> tuple[list[dict[str, Any]], dict[str, dict[str, int]]]:
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

    per_game_stats = build_per_game_stats(player_stats_tags, teams_games)
    total_stats = build_total_stats(player_stats_tags)

    return per_game_stats, total_stats
