from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
import json
from db.pydantic_schemas import AddTag, TagSchema
from db.models import Tag, ShotResult, ShotType, ShotResultTypes, ShotTypeTypes
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
    received_tag = tag_data.tag

    shot_location = received_tag["location"]
    if not ((0 <= shot_location["x"] <= 100) and (0 <= shot_location["y"] <= 100)):
        print(f"Invalid shot location: {shot_location}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad coordinates")

    shot_result_enum = ShotResultTypes.from_string(received_tag["shot_result"])
    shot_result_ref = db_session.query(ShotResult).filter(ShotResult.value == shot_result_enum).first()
    if not shot_result_ref:
        print(f"Invalid shot result: {received_tag['shot_result']}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad shot result")

    if received_tag["shot_type"]:
        shot_type_enum = ShotTypeTypes.from_string(received_tag["shot_type"])
        shot_type_ref = db_session.query(ShotType).filter(ShotType.value == shot_type_enum).first()
        if not shot_type_ref:
            print(f"Invalid shot type: {received_tag['shot_type']}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad shot type")
    else:
        shot_type_ref = None

    try:
        new_tag = Tag(
            ice_x=shot_location["x"],
            ice_y=shot_location["y"],
            shot_result=shot_result_ref,
            shot_type=shot_type_ref
        )

        db_session.add(new_tag)
        db_session.commit()

    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error recording the tag to db.")


    return {"success": True}

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