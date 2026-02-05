from fastapi import Depends, APIRouter, Response
from openpyxl import load_workbook
from sqlalchemy.orm import Session

from db.db_manager import get_db_session
from db.models import Team, User
from utils import get_current_user_and_team

from routes.excel.player_stats.workbook_writer import write_player_sheets
from routes.excel.excel_utils import workbook_to_bytesio
from routes.excel.player_stats.stat_collectors import add_player_stats
from routes.excel.player_stats.players_to_analyze import get_players_to_analyze

router = APIRouter()


@router.get("/player-stats")
async def get_player_scoring_excel(game_ids: str | None = None, db_session: Session = Depends(get_db_session), user_and_team: tuple["User", "Team"] = Depends(get_current_user_and_team)):
    # 1. Get a data structure containing all the players for the seleceted games
    _, team = user_and_team
    players_to_analyze = get_players_to_analyze(game_ids, team, db_session)

    # 2. Edit players_to_analyze in place to record their stats for the selected games
    add_player_stats(players_to_analyze)

    # 3. Create the excel file and create + write a sheet with stats for each player
    workbook = load_workbook("excels/players_summary_template.xlsx")    
    write_player_sheets(workbook, players_to_analyze)
    output = workbook_to_bytesio(workbook)

    # 4. Send the output (excel file) as a response
    return Response(
        content=output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=pelaajayhteenveto.xlsx"}
    )
