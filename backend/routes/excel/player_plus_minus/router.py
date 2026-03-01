from fastapi import Depends, APIRouter, Response
from sqlalchemy.orm import Session

from utils import get_current_user_and_team

from db.db_manager import get_db_session
from db.models import Team, User

from routes.excel.player_plus_minus.workbook_writer import build_workbook
from routes.excel.player_plus_minus.get_stats import get_games_with_rosters, get_players_with_stats

router = APIRouter()


@router.get("/plusminus")
async def get_plusminus_excel(game_ids: str, db_session: Session = Depends(get_db_session), user_and_team: tuple["User", "Team"] = Depends(get_current_user_and_team)):
    """Generate plus/minus Excel report for selected games."""
    _, team = user_and_team

    # 1. Load the players in roster for this game, and PlusMinusTags for them
    players = get_players_with_stats(game_ids, team, db_session)

    # 2. Load the game objects with in_roster objects eagerly loaded
    games = get_games_with_rosters(game_ids, team, db_session)

    # 3. Write the total and game sheets and return the workbook as BytesIO object
    output = build_workbook(players, games)

    return Response(content=output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=plusminus.xlsx"})
