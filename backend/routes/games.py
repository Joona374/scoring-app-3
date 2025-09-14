from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Literal

from db.pydantic_schemas import GameCreate, PlayerResponse
from db.db_manager import get_db_session
from db.models import Player, User, Game, GameInRoster
from utils import get_current_user_id
from roster_scraper.roster_scraper import scrape_team_slots

router = APIRouter(
    prefix="/games",
    tags=["games"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create")
def create_game(data: GameCreate, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    user = db_session.query(User).filter(User.id == current_user_id).first()

    new_game = Game(
        date=data.game_date,
        opponent=data.opponent,
        home=data.home_game,
        team=user.team,
        powerplays=data.powerplays,
        penalty_kills=data.penalty_kills
    )
    
    for position in data.players_in_roster:
        if position.player:
            new_game_in_roster = GameInRoster(
                line=position.line,
                position=position.position,
                player_id=position.player.id
            )
            new_game.in_rosters.append(new_game_in_roster)
    try:
        db_session.add(new_game)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=500, detail=f"Creating a game failed: {str(e)}")

    return {"game_id": new_game.id}

@router.delete("/delete/{game_id}")
def delete_game(game_id: int, already_confirmed: bool, db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    user = db_session.query(User).filter(User.id == current_user_id).first()
    game = db_session.query(Game).filter(Game.id == game_id).first()
    if user.team != game.team:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No permission to delete this game")

    if not already_confirmed and (len(game.player_stats_tags) > 0 or len(game.team_stats_tags) > 0):
        return {"challenge": True, "team_tags": len(game.team_stats_tags), "player_tags": len(game.player_stats_tags), "goalie_tags": 0} # TODO: Add actual number of goalie tags once they are created

    try:
        db_session.delete(game)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        print(e)
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

    return {"message": "Game deleted successfully", "success": True, "challenge": False, "game_id": game_id}
# TODO THIS CRASHES FOR SOME REASON.

@router.get("/get-for-user")
def create_game(db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    try:
        user = db_session.query(User).filter(User.id == current_user_id).first()
        games = db_session.query(Game).filter(Game.team == user.team).all()
        return games
    except Exception as e:
        print(f"Error getting games: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed getting the games for user: {e}")

@router.get("/scrape-roster")
async def scrape_roster(game_url: str, home: Literal["home", "away"], db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    print(f"Attempting to scrape game with url: {game_url}")
    roster = await scrape_team_slots(game_url, home)
    user = db_session.query(User).filter(User.id == current_user_id).first()
    players_in_team = db_session.query(Player).filter(Player.team == user.team).all()
    
    roster_response = {}
    for position, player_name in roster.items():
        player = find_player_by_name(players_in_team, player_name)
        
        if player:
            player_response = PlayerResponse(
                id=player.id,
                first_name=player.first_name,
                last_name=player.last_name,
                jersey_number=player.jersey_number,
                position=player.position.name
            )
            roster_response[position] = player_response

    return roster_response

def find_player_by_name(players_in_team: list[Player], player_name: str) -> Player | None:
    first_name, last_name = player_name.split(" ")
    for player in players_in_team:
        if player.first_name == first_name and player.last_name == last_name:
            return player