from models import Base
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
######### FOR FORCEFULLY EMPTYING THE DB. ADD NEEDED TABLE NAMES ########
# print("Attempting to forcefully drop tables with CASCADE...")
# with engine.connect() as connection:
#     # We use text() to tell SQLAlchemy this is a literal SQL command.
#     # CASCADE tells PostgreSQL to drop dependent objects (like constraints) too.
#     connection.execute(text("DROP TABLE IF EXISTS users, teams CASCADE;"))
#     connection.commit() # Make sure the transaction is committed
# print("Forceful drop successful.")

if __name__ == "__main__":
    print("\nFirst dropping all existing tables...")
    Base.metadata.drop_all(engine)

    print("Creating tables...")
    Base.metadata.create_all(engine)
    print("Created the following tables:")
    for table in Base.metadata.sorted_tables:
        print(f"- {table.name}")
    print("Tables created successfully.")