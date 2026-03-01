from fastapi import APIRouter

from routes.players.routes.for_team import router as for_team_router
from routes.players.routes.delete import router as delete_router
from routes.players.routes.create import router as create_router
from routes.players.routes.update import router as update_router

router = APIRouter(
    prefix="/players",
    tags=["players"],
    responses={404: {"description": "Not found"}},
)

router.include_router(for_team_router)
router.include_router(delete_router)
router.include_router(create_router)
router.include_router(update_router)
