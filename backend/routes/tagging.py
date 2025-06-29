from pathlib import Path
from fastapi import APIRouter
import json

router = APIRouter(
    prefix="/tagging",
    tags=["tagging"],
    responses={404: {"description": "Not found"}},
)

@router.get("/test")
def test_tagging():
    return "Hello :D"

@router.get("/questions")
def get_questions():
    questions_json_path = Path("./tagging/questions.json")
    text = questions_json_path.read_text()
    parsed_json = json.loads(text)

    return parsed_json