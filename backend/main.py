from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes.dashboard import dashboard_router
from routes.games_router import games_router
from routes.players import players_router
from routes.tagging import tagging_router
from routes.teams import teams_router
from routes.analysis import analysis_router
from routes.auth import auth_router
from routes.admin import admin_router
from routes.excel import excel_router
from routes.users import users_router
import logging
# Load the environment variables from the .env file
load_dotenv()

# Initialize the FastAPI application
app = FastAPI()

# Include all the routers. REMEMBER TO ADD HERE ANY NEW ROUTERS.
app.include_router(users_router.router)
app.include_router(auth_router.router)
app.include_router(teams_router.router)
app.include_router(players_router.router)
app.include_router(tagging_router.router)
app.include_router(admin_router.router)
app.include_router(games_router.router)
app.include_router(excel_router.router)
app.include_router(analysis_router.router)
app.include_router(dashboard_router.router)


# Middleware to handle CORS.
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


# Keepalive endpoint for uptime monitoring services
@app.get("/health")
@app.head("/health")
def health():
    return {"status": "ok"}
