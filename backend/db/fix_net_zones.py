from db.models import PlayerStatsTag
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set or .env not loaded")

print("Using DB:", DATABASE_URL)

engine = create_engine(DATABASE_URL)


def fix_net_zones(db_session: Session):
    tags = db_session.query(PlayerStatsTag).all()
    issues_found = 0

    for tag in tags:
        if tag.net_x >= 65:
            tag.net_width = "Right"
            issues_found += 1

    db_session.commit()
    print(f"✅ Fixed net zones for {issues_found} tags.")


if __name__ == "__main__":
    with Session(engine) as session:
        fix_net_zones(session)
