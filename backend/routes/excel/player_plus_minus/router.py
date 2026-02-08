from fastapi import Depends, APIRouter, Response
from sqlalchemy.orm import Session


from utils import get_current_user_and_team

from db.db_manager import get_db_session
from db.models import Team, User 

from routes.excel.stats_utils import get_selected_games
from routes.excel.player_plus_minus.get_stats import get_plusminus_games_data
from routes.excel.player_plus_minus.workbook_writer import build_plusminus_workbook

router = APIRouter()


@router.get("/plusminus")
async def get_plusminus_excel(game_ids: str | None = None, db_session: Session = Depends(get_db_session), user_and_team: tuple["User", "Team"] = Depends(get_current_user_and_team)):
    _, team = user_and_team

    # 1. Get the game objects based on the selected game_ids
    games = get_selected_games(team, game_ids)

    # 2. Fetch the gama data, and build the data containers
    data_for_games, total_stats = get_plusminus_games_data(games, db_session)

    # 3. Builds the full plusminus workbook, and returns it as BytesIO object.
    output = build_plusminus_workbook(total_stats, data_for_games)

    return Response(content=output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=plusminus.xlsx"})
