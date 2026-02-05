from collections import defaultdict
from io import BytesIO
import copy

from fastapi import Depends, APIRouter, Response
from openpyxl import load_workbook
from sqlalchemy.orm import Session, joinedload

from db.db_manager import get_db_session
from db.models import Team, Player, GameInRoster, Game, PlayerStatsTag, PlayerStatsTagOnIce, PlayerStatsTagParticipating, User, ShotResultTypes
from utils import get_current_user_and_team

router = APIRouter()


########################## FOR PLAYER +/- ##########################
def format_player_name(player: Player, in_rosters: list[GameInRoster]) -> str:
    """
    Formats the player's name as just "LASTNAME" by default.
    If 2 players share the same last name in the given roster,
    format as "LASTNAME F." where F is the first (or multiple if needed) initial.
    """

    players_with_same_lastname = []
    for roster_spot in in_rosters:
        other_player = roster_spot.player
        if other_player.last_name == player.last_name and other_player.id != player.id:
            players_with_same_lastname.append(other_player)

    if not players_with_same_lastname:
        return f"{player.last_name.upper()}"

    initials = player.first_name[0]
    for other_player in players_with_same_lastname:
        for i in range(0, len(other_player.first_name)):
            if initials[i] == other_player.first_name[i]:
                initials += player.first_name[i + 1]
            else:
                break
    return f"{player.last_name.upper()} {initials}."


def build_game_data_structure(game: Game):
    data_structure = {"game_id": game.id, "opponent": game.opponent, "home": game.home, "date": game.date, "roster": {}}
    game_roster = data_structure["roster"]

    for roster_spot in game.in_rosters:
        player = roster_spot.player
        formated_name = format_player_name(player, game.in_rosters)
        player_dict = {
            "name": formated_name,
            "position": player.position.name,
            "stats": {
                "ES-PG+": 0,  # ES-PG+ = Even strengthParticipated Goal +
                "ES-PG-": 0,
                "ES-PC+": 0,
                "ES-PC-": 0,  # PC- = Partcipated chance -
                "ES-OIG+": 0,
                "ES-OIG-": 0,  # OIG- = On ice Goal -
                "ES-OIC+": 0,
                "ES-OIC-": 0,
                "PP-PG+": 0,  # PP-PG+ = Powerplay
                "PP-PG-": 0,
                "PP-PC+": 0,
                "PP-PC-": 0,
                "PP-OIG+": 0,
                "PP-OIG-": 0,
                "PP-OIC+": 0,
                "PP-OIC-": 0,
                "PK-PG+": 0,  # PK-PG+ = Penaltykill
                "PK-PG-": 0,
                "PK-PC+": 0,
                "PK-PC-": 0,
                "PK-OIG+": 0,
                "PK-OIG-": 0,
                "PK-OIC+": 0,
                "PK-OIC-": 0,
            },
        }
        game_roster[player.id] = player_dict

    return data_structure


def convert_roster_to_lists(roster: dict) -> dict:
    listed_roster = {"forwards": [], "defenders": []}

    for player_dict in roster.values():
        if player_dict["position"] == "FORWARD":
            listed_roster["forwards"].append(player_dict)
        elif player_dict["position"] == "DEFENDER":
            listed_roster["defenders"].append(player_dict)

    for group in listed_roster.values():
        group.sort(key=lambda player: player["name"])

    return listed_roster


def get_plusminus_games_data(teams_games: list[Game], db_session: Session):
    """
    Aggregates and processes game and player statistics data for a list of games.
    For each game in the provided list, this function:
    - Collects player statistics tags, on-ice links, and participating links from the database.
    - Maps and aggregates statistics for each player, both per-game and as a total across all games.
    - Handles statistics for different strengths (ES, PP, PK) and result types (goal for/against, chance for/against).
    - Converts roster dictionaries to lists for output compatibility.
    - Sorts the collected game data by date in descending order.
    Args:
        teams_games (list[Game]): List of Game objects to process.
        db_session (Session): SQLAlchemy database session for querying related data.
    Returns:
        tuple:
            - data_collector (list[dict]): List of processed game data dictionaries, one per game.
            - listed_total_data (list[dict]): Aggregated player statistics across all games as a list of dictionaries.
    """

    data_collector = []
    total_stats = {}
    game_ids = [game.id for game in teams_games]

    player_stats_tags = (
        db_session.query(PlayerStatsTag)
        .options(
            joinedload(PlayerStatsTag.shot_result),
            joinedload(PlayerStatsTag.players_on_ice).joinedload(PlayerStatsTagOnIce.player),
            joinedload(PlayerStatsTag.players_participating).joinedload(PlayerStatsTagParticipating.player),
        )
        .filter(PlayerStatsTag.game_id.in_(game_ids))
        .all()
    )
    PSTs_by_game_id = defaultdict(list)
    for tag in player_stats_tags:
        PSTs_by_game_id[tag.game_id].append(tag)

    on_ice_links = db_session.query(PlayerStatsTagOnIce).join(PlayerStatsTag).filter(PlayerStatsTag.game_id.in_(game_ids)).all()
    OILs_by_PST_id = defaultdict(list)  # list of OnIce links with PlayerStatsTag id as key
    for on_ice_link in on_ice_links:
        OILs_by_PST_id[on_ice_link.tag_id].append(on_ice_link)

    participating_links = db_session.query(PlayerStatsTagParticipating).join(PlayerStatsTag).filter(PlayerStatsTag.game_id.in_(game_ids)).all()
    PLs_by_PST_id = defaultdict(list)
    for partic_link in participating_links:
        PLs_by_PST_id[partic_link.tag_id].append(partic_link)

    tag_type_mapping = {
        ShotResultTypes.GOAL_FOR: "G+",
        ShotResultTypes.GOAL_AGAINST: "G-",
        ShotResultTypes.CHANCE_FOR: "C+",
        ShotResultTypes.CHANCE_AGAINST: "C-",
    }

    for game in teams_games:
        game_data = build_game_data_structure(game)
        for id, data in game_data["roster"].items():
            if id not in total_stats:
                total_data = copy.deepcopy(data)
                total_data["GP"] = 1
                total_stats[id] = total_data
            else:
                total_stats[id]["GP"] += 1

        tags = PSTs_by_game_id[game.id]
        for tag in tags:
            strengths = tag.strengths
            if strengths not in ["ES", "PP", "PK"]:
                continue

            if tag.shot_result.value in [ShotResultTypes.SHOT_FOR, ShotResultTypes.SHOT_AGAINST]:
                continue  # Skip shot tags, only process chances and goals

            result_part = tag_type_mapping[tag.shot_result.value]

            tags_on_ice = OILs_by_PST_id[tag.id]
            OI_player_ids = [tag.player.id for tag in tags_on_ice]
            for id in OI_player_ids:
                game_data["roster"][id]["stats"][f"{strengths}-OI{result_part}"] += 1
                total_stats[id]["stats"][f"{strengths}-OI{result_part}"] += 1

            tags_participating = PLs_by_PST_id[tag.id]
            P_player_ids = [tag.player.id for tag in tags_participating]
            for id in P_player_ids:
                game_data["roster"][id]["stats"][f"{strengths}-P{result_part}"] += 1
                total_stats[id]["stats"][f"{strengths}-P{result_part}"] += 1

        game_data["roster"] = convert_roster_to_lists(game_data["roster"])

        data_collector.append(game_data)

    type(data_collector[0]["date"])
    data_collector.sort(key=lambda game: game["date"], reverse=True)
    listed_total_data = convert_roster_to_lists(total_stats)
    return data_collector, listed_total_data


@router.get("/plusminus")
async def get_plusminus_excel(game_ids: str | None = None, db_session: Session = Depends(get_db_session), user_and_team: tuple["User", "Team"] = Depends(get_current_user_and_team)):
    FIRST_DEFENDER_ROW = 4
    FIRST_FORWARD_ROW = 26

    user, team = user_and_team

    teams_games = team.games
    if game_ids:
        split_ids = [int(game_id) for game_id in game_ids.split(",")]
        teams_games = []
        for game in team.games:
            if game.id in split_ids:
                teams_games.append(game)
    else:
        teams_games = team.games

    data_for_games, total_stats = get_plusminus_games_data(teams_games, db_session)

    # Load the excel file and template sheet
    workbook = load_workbook("excels/plus_minus_template.xlsx")
    template_sheet = workbook.worksheets[0]

    stat_column_mapping = {
        "OIG+": "A",  # OIG+ = On ice Goal +
        "OIG-": "B",  # OIG- = On ice Goal -
        "OIC+": "D",  # OIC+ = On ice Chance +
        "OIC-": "E",  # OIC- = On ice Chance -
        "PG+": "H",  # PG+ = Participated Goal +
        "PG-": "I",  # PG- = Participated Goal -
        "PC+": "K",  # PC+ = Participated chance +
        "PC-": "L",  # PC- = Participated chance -
        "ES-OIG+": "A",  # ES = Even Strength
        "ES-OIG-": "B",
        "ES-OIC+": "D",
        "ES-OIC-": "E",
        "ES-PG+": "H",
        "ES-PG-": "I",
        "ES-PC+": "K",
        "ES-PC-": "L",
        "PP-OIG+": "O",  # PP = Powerplay
        "PP-OIG-": "P",
        "PP-OIC+": "R",
        "PP-OIC-": "S",
        "PP-PG+": "V",
        "PP-PG-": "W",
        "PP-PC+": "Y",
        "PP-PC-": "Z",
        "PK-OIG+": "AC",  # PK = Penaltykill
        "PK-OIG-": "AD",
        "PK-OIC+": "AF",
        "PK-OIC-": "AG",
        "PK-PG+": "AJ",
        "PK-PG-": "AK",
        "PK-PC+": "AM",
        "PK-PC-": "AN",
    }
    name_colums = ["G", "U", "AI", "AW"]

    total_sheet = workbook.copy_worksheet(template_sheet)
    total_sheet.title = "TOTAL"
    for i, defender in enumerate(total_stats["defenders"]):
        row = FIRST_DEFENDER_ROW + i
        for name_col in name_colums:
            total_sheet[f"{name_col}{row}"] = defender["name"]
        for key, value in defender["stats"].items():
            column = stat_column_mapping[key]
            total_sheet[f"{column}{row}"] = value

    for i, forward in enumerate(total_stats["forwards"]):
        row = FIRST_FORWARD_ROW + i
        for name_col in name_colums:
            total_sheet[f"{name_col}{row}"] = forward["name"]
        for key, value in forward["stats"].items():
            column = stat_column_mapping[key]
            total_sheet[f"{column}{row}"] = value

    total_avg_sheet = workbook.copy_worksheet(template_sheet)
    total_avg_sheet.title = "TOTAL AVG"
    for i, defender in enumerate(total_stats["defenders"]):
        row = FIRST_DEFENDER_ROW + i
        games_played = defender["GP"]
        for name_col in name_colums:
            total_avg_sheet[f"{name_col}{row}"] = defender["name"]
        for key, value in defender["stats"].items():
            column = stat_column_mapping[key]
            total_avg_sheet[f"{column}{row}"] = value / games_played

    for i, forward in enumerate(total_stats["forwards"]):
        games_played = forward["GP"]
        row = FIRST_FORWARD_ROW + i
        for name_col in name_colums:
            total_avg_sheet[f"{name_col}{row}"] = forward["name"]
        for key, value in forward["stats"].items():
            column = stat_column_mapping[key]
            total_avg_sheet[f"{column}{row}"] = value / games_played

    for game in data_for_games:
        game_sheet = workbook.copy_worksheet(template_sheet)

        if "/" in game["opponent"]:
            sanitized_opponent = game["opponent"].replace("/", "&")
            game_sheet.title = f"{sanitized_opponent} {game['date']}"
        else:
            game_sheet.title = f"{game["opponent"]} {game["date"]}"

        for i, defender in enumerate(game["roster"]["defenders"]):
            row = FIRST_DEFENDER_ROW + i
            for name_col in name_colums:
                game_sheet[f"{name_col}{row}"] = defender["name"]
            for key, value in defender["stats"].items():
                column = stat_column_mapping[key]
                game_sheet[f"{column}{row}"] = value

        for i, forward in enumerate(game["roster"]["forwards"]):
            row = FIRST_FORWARD_ROW + i
            for name_col in name_colums:
                game_sheet[f"{name_col}{row}"] = forward["name"]
            for key, value in forward["stats"].items():
                column = stat_column_mapping[key]
                game_sheet[f"{column}{row}"] = value

    # Delete template sheet
    workbook.remove(workbook.worksheets[0])

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return Response(content=output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=plusminus.xlsx"})


########################## FOR PLAYER +/- ##########################
