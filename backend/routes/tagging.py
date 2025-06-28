from fastapi import APIRouter

router = APIRouter(
    prefix="/tagging",
    tags=["tagging"],
    responses={404: {"description": "Not found"}},
)

@router.get("/test")
def test_tagging():
    return "Hello :D"

# TODO: Serve questions.json to React frontend
# - Create GET endpoint (e.g. /api/questions)
# - Load and return the questions from questions.json
# - Later: support custom question sets if needed (query param or user-specific)
