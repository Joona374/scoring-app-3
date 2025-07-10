from fastapi import APIRouter, Response, Depends
from sqlalchemy.orm import Session
from io import BytesIO
from openpyxl import load_workbook
from collections import defaultdict

from utils import get_current_user_id
from db.db_manager import get_db_session
from db.models import TeamStatsTag, User, Game, PlayerStatsTag, ShotResult, ShotResultTypes, PlayerStatsTagOnIce, PlayerStatsTagParticipating

router = APIRouter(
    prefix="/excel",
    tags=["excel"],
    responses={404: {"description": "Not found"}},
)

@router.get("/download-test")
async def download_excel():
    workbook = load_workbook("mock_excel.xlsx")
    player_template = workbook.active

    names = ["Pekka", "Tero", "Pasi", "Harri", "Kari"]

    for i in range(5):
        new_sheet = workbook.copy_worksheet(player_template)
        new_sheet.title = names[i]
        new_sheet["B1"] = names[i]
        new_sheet["D1"] = i * 2

    workbook.remove(workbook.worksheets[0])

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=stats.xlsx"}
    )


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
    
def get_chance_row(scoring_chance: TeamStatsTag):
    try:
        CHANCE_ROW_MAPPING = {
            "rush_type1": {
                "Tasavoimainen": 10,
                "Ylivoimainen": 11,
                "Alivoimainen": 12,
                "Läpiajo": 13
                },

            "takeaway_type": {
                "HAPP/PAHP": 15,
                "KAPP/KAHP": 17,
                "PAPP/HAHP": 19,
                "Jatkopaine": 21,
            },

            "hahp_papp_type": {
                "Täyttö": 23,
                "Alapeli": 25,
                "Yläpeli": 27
            },

            "rebound_type": {
                "SHP": 29,
                "Riisto/Menetys": 29,
                "HAHP/PAPP": 29,
            },

            "faceoff_type": {
                "Hyökkäysalue": 31,
                "Keskialue": 31,
                "Puoulustusalue": 31,
            },

            "v5v5_other_type": {
                "IM": 33,
                "TM": 33,
                "4v4": 33,
            },

            "pp_faceoff_entry_type": {
                "Aloitus Vasen": 38,
                "Aloitus Oikea": 38,
                "Haku / vastaanotto": 38
            },

            "pp_shot_deflection_low_type1": {
                "Päädystä": 40,
                "Siiveltä": 41,
                "Keskeltä": 42,
                "Viivasta": 43
            },

            "pp_blueline_shot_type": {
                "Suora": 45,
                "Ohjuri": 45,
                "Rebound": 45
            },

            "pp_pressure_brokenplay_type": {
                "Paine": 47,
                "Riisto": 47,
                "Brokenplay": 47
            },

            "pp_other_type": {
                "Kuljetus": 49,
                "Punnerrus": 49,
                "Rebound": 49
            },

            "pp_5vs3_type": {
                "Suora": 51,
                "Ohjuri": 51,
                "Rebound": 51
            },

            "pp_av_yv_type": {
                "Läpiajo": 53,
                "YV": 53,
                "TV": 53
            },

            "v3vs3_type": {
                "Aloitus": 58,
                "Hallinta": 58,
                "Riisto / Menetys": 58
            },

            "ps_type": {
                "Laukaus": 60,
                "Harhautus": 60,
                "Muu": 60
            },
            }
        
        for row_name in CHANCE_ROW_MAPPING.keys():
            value = getattr(scoring_chance, row_name, None)
            if value:
                return CHANCE_ROW_MAPPING[row_name][value]
    except Exception as e:
        print(f"Error in get_chance_row with tag:\n{scoring_chance}\nError:{e}")

def get_chance_column(scoring_chance: TeamStatsTag):
    final_columns = [
        "rush_type2", "takeaway_happ_pahp_type", "takeaway_kapp_kahp_type", "takeaway_papp_hahp_type", 
        "takeaway_jatkopaine_type", "hahp_papp_taytto_type", "hahp_papp_alapeli_type", 
        "hahp_papp_ylapeli_type", "rebound_type", "faceoff_type", "v5v5_other_type", 
        "pp_faceoff_entry_type", "pp_shot_deflection_low_type2", "pp_blueline_shot_type", 
        "pp_pressure_brokenplay_type", "pp_other_type", "pp_5vs3_type", "pp_av_yv_type", "v3vs3_type", "ps_type"]
    
    g_columns = ["PAHP", "1. Paine", "Syöttö", "Pohja", "Murtautuminen", "Syöttö sisään", "Suora", "SHP", "Hyökkäysalue", 
                 "IM", "Aloitus Vasen", "Kesk. Pääty.", "Paine", "Kuljetus YV", "Läpiajo", "Aloitus", "Laukaus"]
    h_columns = ["KAHP", "2. Paine", "Kuljetus", "Half Board", "Syöttö 3", "Murtautuminen sisään", "Ohjaus", "Riisto/Menetys", 
                 "Keskialue", "TM", "Aloitus Oikea", "Vasen Siipi", "Ohjuri", "Riisto", "Punnerrus", "Ohjuri", "YV", "Hallinta", "Harhautus"]
    i_columns = ["Kääntö", "3. / Puolustajan Paine", "Muu", "Viiva", "Syöttö 4/5", "HAHP/PAPP", "Puolustusalue", "4v4", 
                 "Haku / vastaanotto", "Oikea siipi", "Rebound", "Brokenplay", "TV", "Riisto / Menetys"]

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
                print(scoring_chance)
                print(f"This is probelm: {value}")
                raise ValueError("COLUMN NOT FOUND ANYWHERE SOS! :D")

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
async def get_teamstats_excel(db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):

    user = db_session.query(User).filter(User.id == current_user_id).first()

    # Get all the tag wit db query
    all_tags = db_session.query(TeamStatsTag).filter(TeamStatsTag.game.has(team=user.team)).all()

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
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=stats.xlsx"}
    )
########################## FOR TEAM STATS ##########################


########################## FOR PLAYER +/- ##########################
def build_game_data_structure(game: Game):
    data_structure = {
        "game_id": game.id,
        "opponent": game.opponent,
        "home": game.home,
        "date": game.date,
        "roster": {}}
    game_roster = data_structure["roster"]

    for roster_spot in game.in_rosters:
        player = roster_spot.player
        player_dict = {
            "name": f"{player.last_name.upper()} {player.first_name}",
            "position": player.position.name,
            "stats": {
                "ES-PG+": 0,   # ES-PG+ = Even strengthParticipated Goal +
                "ES-PG-": 0,
                "ES-PC+": 0,   
                "ES-PC-": 0,   # PC- = Partcipated chance -
                "ES-OIG+": 0,  
                "ES-OIG-": 0,  # OIG- = On ice Goal -
                "ES-OIC+": 0, 
                "ES-OIC-": 0,
                "PP-PG+": 0,   # PP-PG+ = Powerplay
                "PP-PG-": 0,
                "PP-PC+": 0,   
                "PP-PC-": 0,   
                "PP-OIG+": 0,  
                "PP-OIG-": 0,  
                "PP-OIC+": 0, 
                "PP-OIC-": 0,
                "PK-PG+": 0,   # PK-PG+ = Penaltykill
                "PK-PG-": 0,
                "PK-PC+": 0,   
                "PK-PC-": 0,
                "PK-OIG+": 0,  
                "PK-OIG-": 0,  
                "PK-OIC+": 0, 
                "PK-OIC-": 0
            }
        }
        game_roster[player.id] = player_dict

    return data_structure

def convert_roster_to_lists(roster: dict) -> dict:
    listed_roster = {
        "forwards": [],
        "defenders": []
    }

    for player_dict in roster.values():
        if player_dict["position"] == "FORWARD":
            listed_roster["forwards"].append(player_dict)
        elif player_dict["position"] == "DEFENDER":
            listed_roster["defenders"].append(player_dict)

    for group in listed_roster.values():
        group.sort(key=lambda player: player["name"])

    return listed_roster


def get_games_data(teams_games: list[Game], db_session: Session):
    """
    Aggregates and processes game data for a list of games, including player statistics and participation details.
    Args:
        teams_games (list[Game]): List of Game objects to process.
        db_session (Session): SQLAlchemy database session for querying related data.
    Returns:
        list[dict]: A list of dictionaries, each representing processed data for a game, including roster statistics and metadata.
    Raises:
        KeyError: If expected keys are missing in the roster or tag mappings.
        AttributeError: If expected attributes are missing from queried objects.
    Notes:
        - The function collects player statistics tags, on-ice links, and participating links for the provided games.
        - It maps shot result types to custom string representations (e.g., "G+", "C-").
        - Player statistics are aggregated per game and per player, distinguishing between on-ice and participating roles.
        - The resulting list is sorted by game date in descending order.
    """
    data_collector = []
    game_ids = [game.id for game in teams_games]

    player_stats_tags = db_session.query(PlayerStatsTag).filter(PlayerStatsTag.game_id.in_(game_ids)).all()
    PSTs_by_game_id = defaultdict(list)
    for tag in player_stats_tags:
        PSTs_by_game_id[tag.game_id].append(tag)

    on_ice_links = db_session.query(PlayerStatsTagOnIce).join(PlayerStatsTag).filter(PlayerStatsTag.game_id.in_(game_ids)).all()  
    OILs_by_PST_id = defaultdict(list) # list of OnIce links with PlayerStatsTag id as key
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
        tags = PSTs_by_game_id[game.id]
        for tag in tags:
            strengths = tag.strengths
            if strengths not in ["ES", "PP", "PK"]:
                continue

            result_part = tag_type_mapping[tag.shot_result.value]
            
            tags_on_ice = OILs_by_PST_id[tag.id]
            OI_player_ids = [tag.player.id for tag in tags_on_ice]
            for id in OI_player_ids:
                game_data["roster"][id]["stats"][f"{strengths}-OI{result_part}"] += 1

            tags_participating = PLs_by_PST_id[tag.id]
            P_player_ids = [tag.player.id for tag in tags_participating]
            for id in P_player_ids:
                game_data["roster"][id]["stats"][f"{strengths}-P{result_part}"] += 1


        game_data["roster"] = convert_roster_to_lists(game_data["roster"])

        data_collector.append(game_data)
    
    type(data_collector[0]["date"])
    data_collector.sort(key=lambda game: game["date"], reverse=True)
    return data_collector


@router.get("/plusminus")
async def get_teamstats_excel(db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):

    user = db_session.query(User).filter(User.id == current_user_id).first()
    team = user.team
    teams_games = team.games

    data_for_games = get_games_data(teams_games, db_session)
    print(data_for_games)

    # Load the excel file and template sheet
    workbook = load_workbook("excels/plus_minus_template.xlsx")
    template_sheet = workbook.worksheets[0]

    stat_column_mapping = {
            "OIG+": "A",  
            "OIG-": "B",  # OIG- = On ice Goal -
            "OIC+": "D", 
            "OIC-": "E",
            "PG+": "H",   # PG+ = Participated Goal +
            "PG-": "I",
            "PC+": "K",   
            "PC-": "L",   # PC- = Partcipated chance -


            "ES-OIG+": "A",  
            "ES-OIG-": "B",  # OIG- = On ice Goal -
            "ES-OIC+": "D", 
            "ES-OIC-": "E",
            "ES-PG+": "H",   # ES-PG+ = Even strengthParticipated Goal +
            "ES-PG-": "I",
            "ES-PC+": "K",   
            "ES-PC-": "L",   # PC- = Partcipated chance -

            "PP-OIG+": "O",  
            "PP-OIG-": "P",  
            "PP-OIC+": "R", 
            "PP-OIC-": "S",
             "PP-PG+": "V",   # PP-PG+ = Powerplay
            "PP-PG-": "W",
            "PP-PC+": "Y",   
            "PP-PC-": "Z",   
   
            "PK-OIG+": "AC",  
            "PK-OIG-": "AD",  
            "PK-OIC+": "AF", 
            "PK-OIC-": "AG",
            "PK-PG+": "AJ",   # PK-PG+ = 
            "PK-PG-": "AK",
            "PK-PC+": "AM",   
            "PK-PC-": "AN"
    }
    name_colums = ["G", "U", "AI","AW"]

    for game in data_for_games:
        game_sheet = workbook.copy_worksheet(template_sheet)
        game_sheet.title = f"{game["opponent"]} {game["date"]}"

        for i, defender in enumerate(game["roster"]["defenders"]):
            row = 4 + i
            for name_col in name_colums:
                game_sheet[f"{name_col}{row}"] = defender["name"]
            for key, value in defender["stats"].items():
                column = stat_column_mapping[key]
                game_sheet[f"{column}{row}"] = value

        for i, forward in enumerate(game["roster"]["forwards"]):
            row = 18 + i
            for name_col in name_colums:
                game_sheet[f"{name_col}{row}"] = forward["name"]
            for key, value in forward["stats"].items():
                column = stat_column_mapping[key]
                game_sheet[f"{column}{row}"] = value

            

    # # Write sheets for individual games
    # for _, tags_list in games_with_stats_dict.items():
    #     game_object = tags_list[0].game
    #     game_sheet = workbook.copy_worksheet(team_stats_sheet)
    #     game_sheet.title = f"{game_object.opponent} {game_object.date}"
    #     cell_values_for_game = calculate_numbers_for_cells(tags_list)
    #     for cell, value in cell_values_for_game.items():
    #         game_sheet[cell] = int(value)

    # Delete template sheet
    workbook.remove(workbook.worksheets[0])

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=stats.xlsx"}
    )




########################## FOR PLAYER +/- ##########################