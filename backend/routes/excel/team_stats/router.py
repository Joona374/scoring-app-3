from collections import defaultdict

from fastapi import Depends, APIRouter, Response
from openpyxl import load_workbook
from sqlalchemy.orm import Session

from utils import get_current_user_and_team
from db.db_manager import get_db_session
from db.models import User, Team 
from routes.excel.stats_utils import get_selected_games
from routes.excel.excel_utils import workbook_to_bytesio
from routes.excel.team_stats.get_stats import get_team_stats_tags, get_games_stats_dict
from routes.excel.team_stats.workbook_writer import write_total_sheet, write_game_sheets

router = APIRouter()


@router.get("/teamstats")
async def get_teamstats_excel(game_ids: str, db_session: Session = Depends(get_db_session), user_and_team: tuple["User", "Team"] = Depends(get_current_user_and_team)):
    _, team = user_and_team
    games = get_selected_games(team, game_ids)

    print("games: ", game_ids)

    # 1. Get the team_stats_tags for the selected games
    all_tags = get_team_stats_tags(games, db_session)

    # 2. Build a data container for per game stats, shape: defaultdict[game_id, list[TeamStatsTag]
    games_stats_dict = get_games_stats_dict(all_tags)

    # 3. Load the excel workbook
    workbook = load_workbook("excels/team_stats_template.xlsx")

    # 4. Write the totals stats to the workbook (edits workbook in place)
    write_total_sheet(all_tags, workbook)

    # 5. Write the per game stats on separate sheets to the workbook (edits workbook in place)
    write_game_sheets(games_stats_dict, workbook)

    # 6. Delete template sheet
    workbook.remove(workbook.worksheets[0])

    # 7. Convert the workbook to a BytesIO object to return
    output = workbook_to_bytesio(workbook)

    return Response(
        content=output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=joukkuetilastot.xlsx"}
    )


########################## FOR TEAM STATS ##########################
