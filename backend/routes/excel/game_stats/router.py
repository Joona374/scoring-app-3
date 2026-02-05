from io import BytesIO

from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, Response

from db.models import User, Team
from db.db_manager import get_db_session
from utils import get_current_user_and_team

from routes.excel.game_stats.get_stats import get_game_stats
from routes.excel.game_stats.game_stats_utils import get_filtered_team_games
from routes.excel.game_stats.workbook_writers import create_game_stats_workbook

router = APIRouter()


@router.get("/game-stats")
async def get_team_scoring_excel(game_ids: str | None = None, db_session: Session = Depends(get_db_session), user_and_team: tuple["User", "Team"] = Depends(get_current_user_and_team)):
    _, team = user_and_team

    teams_games = get_filtered_team_games(team, game_ids)

    per_game_stats, total_stats = get_game_stats(teams_games, db_session)

    workbook = create_game_stats_workbook(total_stats, per_game_stats)

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return Response(
        content=output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=pelitilastot.xlsx"}
    )
