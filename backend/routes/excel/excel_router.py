from fastapi import APIRouter

###### Import and include the sub-routes on the /excel router ######
from routes.excel.game_stats.router import router as game_stats_router
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
