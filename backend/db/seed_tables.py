from db.models import ShotResult, ShotResultTypes, ShotType, ShotTypeTypes
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import os

def seed_shot_results(db_session: Session):
    new_results = []
    for shot_result_type in ShotResultTypes:
        exists_already = db_session.query(ShotResult).filter(ShotResult.value == shot_result_type).first()
        if exists_already:
            continue
        result = ShotResult(value=shot_result_type)
        new_results.append(result)

    db_session.add_all(new_results)
    print(f"Added {len(new_results)} new shot results.")

def seed_shot_types(db_session: Session):
    new_types = []
    for shot_type_type in ShotTypeTypes:
        exists_already = db_session.query(ShotType).filter(ShotType.value == shot_type_type).first()
        if exists_already:
            continue
        type = ShotType(value=shot_type_type)
        new_types.append(type)

    db_session.add_all(new_types)
    print(f"Added {len(new_types)} new shot types.")

def main():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        engine = create_engine(DATABASE_URL)
    else:
        print("ERROR CREATING A ENGINE IN seed_tables.py")
        return "EN JAKSA RAISEE ON LAISKA MUTTA SOS :D"

    db_session = Session(engine)
    try:
        seed_shot_results(db_session)
        seed_shot_types(db_session)
        db_session.commit()
    finally:
        db_session.close()

if __name__ == "__main__":
    main()