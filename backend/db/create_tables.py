from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import random
import string

from .models import Base, RegCode  # Import your model
from .seed_tables import main as seed_tables

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)

def force_drop_tables():
    ######### FOR FORCEFULLY EMPTYING THE DB. ADD NEEDED TABLE NAMES ########
    print("Attempting to forcefully drop tables with CASCADE...")
    with engine.connect() as connection:
        # We use text() to tell SQLAlchemy this is a literal SQL command.
        # CASCADE tells PostgreSQL to drop dependent objects (like constraints) too.
        connection.execute(text("DROP TABLE IF EXISTS users, teams, reg_codes, players, shot_results, shot_types, tags, games, games_in_roster CASCADE;"))
        connection.commit() # Make sure the transaction is committed
    print("Forceful drop successful.")

def add_creator_code():
    """
    Generates a random 6-character creator code consisting of uppercase letters and digits,
    creates a new RegCode instance with this code (marked as a creation code), adds it to the database,
    commits the transaction, and returns the generated code.
    Returns:
        str: The generated 6-character creator code.
    """

    Session = sessionmaker(bind=engine)
    session = Session()
    
    random_code = ""
    for _ in range(6):
        random_code += random.choice(string.ascii_uppercase + string.digits + string.digits)

    test_code = RegCode(
        code=random_code,
        creation_code=True,
        join_code=False,
        team_related_id=None
    )
    
    session.add(test_code)
    session.commit()
    session.close()

    print(f"Seeded creator code: {random_code}")
    return random_code

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

    random_code = add_creator_code()

    seed_tables()

    print("Tables created successfully.")

    return random_code


if __name__ == "__main__":
    main()