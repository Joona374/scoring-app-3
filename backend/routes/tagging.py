from pathlib import Path
from fastapi import APIRouter, Depends
import json
from db.pydantic_schemas import AddTag, Tag
from db.db_manager import get_db_session
from sqlalchemy.orm import Session
from utils import get_current_user_id

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

@router.post("/add-tag")
def add_tag(tag_data: AddTag, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    print(tag_data.tag)

    final_tag: Tag = tag_data.tag
    print(final_tag.location)

    return "Hello?"

# TODO LIST FOR TAG RECORDING:
# 
# COMPLETED:
# ✓ Created reference tables (ShotResult, ShotType) with enums
# ✓ Built seeding system to populate reference tables
# ✓ Set up basic route structure for receiving tag data
#
# NEXT STEPS:
# 1. VALIDATION & CONVERSION:
#    - Convert frontend strings ("Maali +") to database IDs 
#    - Need lookup functions: get_shot_result_id("Maali +") -> returns DB ID
#    - Handle validation errors (what if frontend sends "Maali +" but DB has "Maali +"?)
#    - Validate required fields exist (location, shot_result, shot_type)
#
# 2. CREATE MAIN TAG TABLE:
#    - Design Tag model that references ShotResult & ShotType by foreign key
#    - Include location (x,y coordinates), user_id, timestamp
#    - Decide: separate columns vs JSON storage for flexibility
#
# 3. SAVE TO DATABASE:
#    - Create Tag instance with converted IDs
#    - Save to database with proper error handling
#
# 4. TESTING:
#    - Test with real frontend data
#    - Handle edge cases (missing fields, invalid values)
#
# CURRENT ISSUE: Line 23-24 won't work because tag_data.tag is dict, not Tag model