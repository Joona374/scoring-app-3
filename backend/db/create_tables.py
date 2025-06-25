from models import Base, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from sqlalchemy.exc import OperationalError

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

if __name__ == "__main__":
    print("\nFirst dropping all existing tables...")
    Base.metadata.drop_all(engine)

    print("Creating tables...")
    Base.metadata.create_all(engine)
    print("Created the following tables:")
    for table in Base.metadata.sorted_tables:
        print(f"- {table.name}")
    print("Tables created successfully.")