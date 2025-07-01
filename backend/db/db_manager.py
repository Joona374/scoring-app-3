from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os
from sqlalchemy.exc import OperationalError

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
	raise ValueError("DATABASE_URL environment variable is not set.")

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
	db_session: Session = SessionLocal()
	try:
		yield db_session		
	finally:
		db_session.close()

def test_connection():
	try:
		with engine.connect() as connection:
			print("✅ Connection to database successful!")
	except OperationalError as e:
		print("❌ Database connection failed:")
		print(e)