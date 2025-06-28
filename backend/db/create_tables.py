from models import Base
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import RegCode  # Import your model
from dotenv import load_dotenv
import os
import random
import string

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
        connection.execute(text("DROP TABLE IF EXISTS users, teams, reg_codes, registration_codes CASCADE;"))
        connection.commit() # Make sure the transaction is committed
    print("Forceful drop successful.")

def add_creator_code():
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

if __name__ == "__main__":
    force_drop_tables()

    print("\nFirst dropping all existing tables...")
    Base.metadata.drop_all(engine)

    print("Creating tables...")
    Base.metadata.create_all(engine)
    
    print("Created the following tables:")
    for table in Base.metadata.sorted_tables:
        print(f"- {table.name}")

    add_creator_code()



    print("Tables created successfully.")