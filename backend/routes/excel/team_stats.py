from collections import defaultdict
from io import BytesIO

from fastapi import Depends, APIRouter, Response
from openpyxl import load_workbook
from sqlalchemy.orm import Session

from db.db_manager import get_db_session
from db.models import Team, TeamStatsTag, User
from utils import get_current_user_and_team

router = APIRouter()

########################## FOR TEAM STATS ##########################
def get_result_column_shifter(scoring_chance: TeamStatsTag):
    if scoring_chance.play_result == "Maali +":
        return 0
    elif scoring_chance.play_result == "Maali -":
        return 3
    elif scoring_chance.play_result == "MP +":
        return 6
    elif scoring_chance.play_result == "MP -":
        return 9
    else:
        raise ValueError("Invalid play_result in scoring_chance", scoring_chance)


def get_chance_row(scoring_chance: TeamStatsTag):
    try:
        CHANCE_ROW_MAPPING = {
            "rush_type1": {"Tasavoimainen": 10, "Ylivoimainen": 11, "Alivoimainen": 12, "Läpiajo": 13},
            "takeaway_type": {
                "HAPP/PAHP": 15,
                "KAPP/KAHP": 17,
                "PAPP/HAHP": 19,
                "Jatkopaine": 21,
            },
            "hahp_papp_type": {"Täyttö": 23, "Alapeli": 25, "Yläpeli": 27},
            "rebound_type": {
                "SHP": 29,
                "Riisto/Menetys": 29,
                "HAHP/PAPP": 29,
            },
            "faceoff_type": {
                "Hyökkäysalue": 31,
                "Keskialue": 31,
                "Puolustusalue": 31,
            },
            "v5v5_other_type": {
                "IM": 33,
                "TM": 33,
                "4v4": 33,
            },
            "pp_faceoff_entry_type": {"Aloitus Vasen": 38, "Aloitus Oikea": 38, "Haku / vastaanotto": 38},
            "pp_shot_deflection_low_type1": {"Päädystä": 40, "Siiveltä": 41, "Keskeltä": 42, "Viivasta": 43},
            "pp_blueline_shot_type": {"Suora": 45, "Ohjuri": 45, "Rebound": 45},
            "pp_pressure_brokenplay_type": {"Paine": 47, "Riisto": 47, "Brokenplay": 47},
            "pp_other_type": {"Kuljetus": 49, "Punnerrus": 49, "Rebound": 49},
            "pp_5vs3_type": {"Suora": 51, "Ohjuri": 51, "Rebound": 51},
            "pp_av_yv_type": {"Läpiajo": 53, "YV": 53, "TV": 53},
            "v3vs3_type": {"Aloitus": 58, "Hallinta": 58, "Riisto / Menetys": 58},
            "ps_type": {"Laukaus": 60, "Harhautus": 60, "Muu": 60},
        }

        for row_name in CHANCE_ROW_MAPPING.keys():
            value = getattr(scoring_chance, row_name, None)
            if value:
                return CHANCE_ROW_MAPPING[row_name][value]
    except Exception as e:
        raise ValueError(f"In get_chance_row: {str(e)}", scoring_chance)  # fmt: skip


def get_chance_column(scoring_chance: TeamStatsTag) -> str:
    final_columns = [
        "rush_type2",
        "takeaway_happ_pahp_type",
        "takeaway_kapp_kahp_type",
        "takeaway_papp_hahp_type",
        "takeaway_jatkopaine_type",
        "hahp_papp_taytto_type",
        "hahp_papp_alapeli_type",
        "hahp_papp_ylapeli_type",
        "rebound_type",
        "faceoff_type",
        "v5v5_other_type",
        "pp_faceoff_entry_type",
        "pp_shot_deflection_low_type2",
        "pp_blueline_shot_type",
        "pp_pressure_brokenplay_type",
        "pp_other_type",
        "pp_5vs3_type",
        "pp_av_yv_type",
        "v3vs3_type",
        "ps_type",
    ]

    g_columns = [
        "PAHP",
        "1. Paine",
        "Syöttö",
        "Pohja",
        "Murtautuminen",
        "Syöttö sisään",
        "Suora",
        "SHP",
        "Hyökkäysalue",
        "IM",
        "Aloitus Vasen",
        "Kesk. / Pääty.",
        "Paine",
        "Kuljetus YV",
        "Läpiajo",
        "Aloitus",
        "Laukaus",
    ]
    h_columns = [
        "KAHP",
        "2. Paine",
        "Kuljetus",
        "Half Board",
        "Syöttö 3:lle",
        "Murtautuminen sisään",
        "Ohjaus",
        "Riisto/Menetys",
        "Keskialue",
        "TM",
        "Aloitus Oikea",
        "Vasen Siipi",
        "Ohjuri",
        "Riisto",
        "Punnerrus",
        "Ohjuri",
        "YV",
        "Hallinta",
        "Harhautus",
    ]
    i_columns = [
        "Kääntö",
        "3. / Puolustajan Paine",
        "Muu",
        "Viiva",
        "Syöttö 4/5:lle",
        "HAHP/PAPP",
        "Puolustusalue",
        "4v4",
        "Haku / vastaanotto",
        "Oikea siipi",
        "Rebound",
        "Brokenplay",
        "TV",
        "Riisto / Menetys",
    ]

    for column in final_columns:
        value = getattr(scoring_chance, column, None)
        if value:
            if value in g_columns:
                return "G"
            elif value in h_columns:
                return "H"
            elif value in i_columns:
                return "I"
            else:
                raise ValueError(f"In get_chance_column: value {value} is not in any column", scoring_chance) # fmt: skip
        # If value is None, continue to next column

    raise RuntimeError("No valid column value found in any final_columns", scoring_chance)


def calculate_numbers_for_cells(all_tags):
    cell_values = {}
    for tag in all_tags:
        row = get_chance_row(tag)
        col = get_chance_column(tag)
        col_shift = get_result_column_shifter(tag)
        shifted_col = chr(ord(col) + col_shift)

        if f"{shifted_col}{row}" in cell_values:
            cell_values[f"{shifted_col}{row}"] += 1
        else:
            cell_values[f"{shifted_col}{row}"] = 1

    return cell_values


@router.get("/teamstats")
async def get_teamstats_excel(game_ids: str, db_session: Session = Depends(get_db_session), user_and_team: tuple["User", "Team"] = Depends(get_current_user_and_team)):

    user, team = user_and_team

    teams_games = team.games
    if game_ids:
        filter_game_ids = [int(game_id) for game_id in game_ids.split(",")]
    else:
        filter_game_ids = [game.id for game in teams_games]

    # Get all the tag wit db query
    all_tags = db_session.query(TeamStatsTag).filter(TeamStatsTag.game.has(team=user.team), TeamStatsTag.game_id.in_(filter_game_ids)).all()

    # Iterate over all_tags to get tags for individual games
    # games_with_stats_dict = {game_id: list[TeamStatsTag]}
    games_with_stats_dict = defaultdict(list)
    for tag in all_tags:
        games_with_stats_dict[tag.game_id].append(tag)

    # Load the excel file and template sheet
    workbook = load_workbook("excels/team_stats_template.xlsx")
    team_stats_sheet = workbook.worksheets[0]

    # Write and calculate the total sheet
    total_sheet = workbook.copy_worksheet(team_stats_sheet)
    total_sheet.title = "TOTAL STATS"
    cell_values = calculate_numbers_for_cells(all_tags)
    for cell, value in cell_values.items():
        total_sheet[cell] = int(value)

    # Write sheets for individual games
    for _, tags_list in games_with_stats_dict.items():
        game_object = tags_list[0].game
        game_sheet = workbook.copy_worksheet(team_stats_sheet)
        if "/" in game_object.opponent:
            sanitized_opponent = game_object.opponent.replace("/", "&")
            game_sheet.title = f"{sanitized_opponent} {game_object.date}"
        else:
            game_sheet.title = f"{game_object.opponent} {game_object.date}"
        cell_values_for_game = calculate_numbers_for_cells(tags_list)
        for cell, value in cell_values_for_game.items():
            game_sheet[cell] = int(value)

    # Delete template sheet
    workbook.remove(workbook.worksheets[0])

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return Response(
        content=output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=joukkuetilastot.xlsx"}
    )


########################## FOR TEAM STATS ##########################
