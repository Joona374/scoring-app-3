from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.create_tables import main as wipe_db
from utils import get_current_user_id, add_creator_code
from db.db_manager import get_db_session
from db.models import User, Team
from db.pydantic_schemas import CreateCode, CreateCodeResponse

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

###### ONLY FOR EMERGENCY USE! ########
# @router.post("/clean-db")
# def clean_db():
#     try:
#         creator_code = wipe_db()
#         return {"Message": "Wiped db!", "creator_code": creator_code}
#     except Exception as e:
#         return {"Message": "DB WIPING FAILED", "ERROR": e}
###### ONLY FOR EMERGENCY USE! ########

###### ONLY FOR EMERGENCY USE! ########
# @router.post("/clean-db")
# def clean_db():
#     try:
#         creator_code = wipe_db()
#         return {"Message": "Wiped db!", "creator_code": creator_code}
#     except Exception as e:
#         return {"Message": "DB WIPING FAILED", "ERROR": e}
###### ONLY FOR EMERGENCY USE! ########

@router.post("/clean-db")
def clean_db(db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    user = db_session.query(User).filter(User.id == current_user_id).first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Non admin user")
    db_session.close()
    try:
        creator_code = wipe_db()
        return {"Message": "Wiped db!", "creator_code": creator_code}
    except Exception as e:
        return {"Message": "DB WIPING FAILED", "ERROR": e}


@router.post("/create-code")
def clean_db(code_data: CreateCode, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    user = db_session.query(User).filter(User.id == current_user_id).first()
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Non admin user")
    
    # try:
    new_code = add_creator_code(admin=False, identifier=code_data.new_code_identifier)
    team_id = new_code.team_related_id
    team = db_session.query(Team).filter(Team.id == team_id).first()
    if team:
        related_team_name = team.name
    else:
        related_team_name = None
    
    response = CreateCodeResponse(
        code=new_code.code,
        used=new_code.used,
        identifier=new_code.identifier,
        creation_code=new_code.creation_code,
        join_code=new_code.join_code,
        admin_code=new_code.admin_code,
        team_related=related_team_name
    )

    return response
    
    # except Exception as e:
    #     print(f"Error creating a code: {e}")
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server side error creating the code.")
