from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

from .models import Base
from .seed_tables import main as seed_tables
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
        # CASCADE tells PostgreSQL to drop dependent objects (like constraints) too.
        connection.execute(text("DROP TABLE IF EXISTS users, teams, reg_codes, players, shot_results, shot_types, tags, games, games_in_roster, team_stats_tags, player_stats_tags, player_stats_tag_on_ice, player_stats_tag_participating CASCADE;"))
        connection.commit() # Make sure the transaction is committed
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

    seed_tables()

    print("Tables created successfully.")

    return new_reg_code.code


if __name__ == "__main__":
    main()