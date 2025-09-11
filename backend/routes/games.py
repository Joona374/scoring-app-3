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
        team=user.team
    )
    
    for position in data.players_in_roster:
        if position.player:
            new_game_in_roster = GameInRoster(
                line=position.line,
                position=position.position,
                player_id=position.player.id
            )
            new_game.in_rosters.append(new_game_in_roster)

    db_session.add(new_game)
    db_session.commit()

    return {"game_id": new_game.id}

@router.get("/get-for-user")
def create_game(db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    user = db_session.query(User).filter(User.id == current_user_id).first()
    games = db_session.query(Game).filter(Game.team == user.team).all()
    return games

@router.get("/scrape-roster")
async def scrape_roster(game_url: str, home: Literal["home", "away"], db_session: Session = Depends(get_db_session), current_user_id: int = Depends(get_current_user_id)):
    roster = await scrape_team_slots(game_url, home)
    user = db_session.query(User).filter(User.id == current_user_id).first()
    players_in_team = db_session.query(Player).filter(Player.team == user.team).all()
    
    roster_response = {}
    for position, player_name in roster.items():
        player = find_player_by_name(players_in_team, player_name)
        
        if player:
            print("Ever here?")
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
    print(first_name, last_name)
    for player in players_in_team:
        print(player)
        if player.first_name == first_name and player.last_name == last_name:
            return player