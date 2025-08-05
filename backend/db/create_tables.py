from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

from db.models import Base
from db.seed_tables import main as seed_tables
from utils import add_creator_code

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)

def force_drop_tables():
    ######### FOR FORCEFULLY EMPTYING THE DB. ADD NEEDED TABLE NAMES ########
    print("Attempting to forcefully drop tables with CASCADE...")
    with engine.connect() as connection:
        print("Connection opens?")
        # Drop tables in reverse dependency order
        tables_to_drop = [
            "player_stats_tag_participating",
            "player_stats_tag_on_ice", 
            "player_stats_tags",
            "team_stats_tags",
            "games_in_roster",
            "games",
            "players",
            "reg_codes",
            "shot_areas",
            "shot_types", 
            "shot_results",
            "users",  # Drop users before teams to break the cycle
            "teams"
        ]
        
        for table in tables_to_drop:
            connection.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
            print(f"Dropped {table}")
        
        connection.commit()
    print("Forceful drop successful.")



def main():
    """
    Drops all existing database tables and recreates them based on the current SQLAlchemy models.
    Prints the progress of dropping and creating tables, lists the created tables, and adds a creator code.
    Returns:
        str: The randomly generated creator code.
    """

    force_drop_tables()

    print("\nFirst dropping all existing tables...")
    Base.metadata.drop_all(engine)

    print("Creating tables...")
    Base.metadata.create_all(engine)
    
    print("Created the following tables:")
    for table in Base.metadata.sorted_tables:
        print(f"- {table.name}")

    new_reg_code = add_creator_code(admin=True, identifier="Initial User")
    new_reg_code = add_creator_code(admin=True, identifier="Initial User")

    seed_tables()

    print("Tables created successfully.")

    return new_reg_code.code
    return new_reg_code.code


if __name__ == "__main__":
    # TO RUN:
    # cd backend 
    # $ python3 -m db.create_tables
    main()