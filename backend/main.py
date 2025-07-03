from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import users, auth, teams, players, tagging, admin, games
import logging
# Load the environment variables from the .env file
load_dotenv()

# Initialize the FastAPI application
app = FastAPI()

# Include all the routers. REMEMBER TO ADD HERE ANY NEW ROUTERS.
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(teams.router)
app.include_router(players.router)
app.include_router(tagging.router)
app.include_router(admin.router)
app.include_router(games.router)


# Middleware to handle CORS. TODO: Make sure to update the regex to match your frontend URL.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https:\/\/scoring-app-3(-git-[\w-]+)?\.vercel\.app|http:\/\/localhost(:\d+)?",
    allow_credentials=True, # Allows cookies to be included in requests
    allow_methods=["*"],    # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allows all headers
)

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Root endpoint to check if the API is live
@app.get("/")
def read_root():
    return {"message": "Scoring App 3.0 API is live!"}
