from fastapi import APIRouter, Response, Depends
from sqlalchemy.orm import Session, joinedload
from io import BytesIO
from openpyxl import load_workbook
from collections import defaultdict

from utils import get_current_user_and_team
from db.db_manager import get_db_session
from db.models import Team, User, PlayerStatsTag, ShotResult, ShotResultTypes, ShotAreaTypes, ShotTypeTypes, PlayerStatsTagOnIce, PlayerStatsTagParticipating


###### Import and include the sub-routes on the /excel router ######
from routes.excel.game_stats import router as game_stats_router
from routes.excel.team_stats import router as team_stats_router
from routes.excel.player_plus_minus import router as player_plus_minus_router
from routes.excel.player_stats import router as player_stats_router

router = APIRouter(
    prefix="/excel",
    tags=["excel"],
    responses={404: {"description": "Not found"}},
)

router.include_router(game_stats_router)
router.include_router(team_stats_router)
router.include_router(player_plus_minus_router)
router.include_router(player_stats_router)
