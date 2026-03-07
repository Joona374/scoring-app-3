from fastapi import APIRouter

from routes.players.endpoints.for_team import router as for_team_router
from routes.players.endpoints.delete import router as delete_router
from routes.players.endpoints.create import router as create_router
from routes.players.endpoints.update import router as update_router
from routes.players.endpoints.stats.stats import router as stats_router

router = APIRouter(
    prefix="/players",
    tags=["players"],
    responses={404: {"description": "Not found"}},
)

router.include_router(for_team_router)
router.include_router(delete_router)
router.include_router(create_router)
router.include_router(update_router)
router.include_router(stats_router)
