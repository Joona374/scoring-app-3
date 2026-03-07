from sqlalchemy.orm import Session
from sqlalchemy import desc

from routes.players.endpoints.stats.maps import get_zone_names
from db.models import PlayerStatsTag, PlayerStatsTagOnIce, PlayerStatsTagParticipating, GameInRoster, Game
from db.pydantic_schema.player_page import PlayerGameMetadata, PlayerTagData


def get_player_all_games(db: Session, player_id: int) -> list[PlayerGameMetadata]:
    roster_entries = db.query(GameInRoster).join(Game).filter(GameInRoster.player_id == player_id).order_by(desc(Game.date)).all()
    
    all_games = []
    for entry in roster_entries:
        all_games.append(PlayerGameMetadata(game_id=entry.game.id, date=str(entry.game.date), opponent=entry.game.opponent, home=entry.game.home))
 
    return all_games


def get_player_tags(db: Session, player_id: int) -> tuple[list[PlayerStatsTag], list[PlayerStatsTag], list[PlayerStatsTag]]:
    shooter_tags = db.query(PlayerStatsTag).filter(PlayerStatsTag.shooter_id == player_id).all()

    on_ice_tag_ids = db.query(PlayerStatsTagOnIce.tag_id).filter(PlayerStatsTagOnIce.player_id == player_id).all()
    on_ice_tag_ids = [t[0] for t in on_ice_tag_ids]
    on_ice_tags = db.query(PlayerStatsTag).filter(PlayerStatsTag.id.in_(on_ice_tag_ids)).all() if on_ice_tag_ids else []
    
    participating_tag_ids = db.query(PlayerStatsTagParticipating.tag_id).filter(PlayerStatsTagParticipating.player_id == player_id).all()
    participating_tag_ids = [t[0] for t in participating_tag_ids]
    participating_tags = db.query(PlayerStatsTag).filter(PlayerStatsTag.id.in_(participating_tag_ids)).all() if participating_tag_ids else []
    
    return shooter_tags, on_ice_tags, participating_tags


def build_all_player_tags(shooter_tags: list[PlayerStatsTag], on_ice_tags: list[PlayerStatsTag], participating_tags: list[PlayerStatsTag]) -> list[PlayerTagData]:
    shooter_ids = {t.id for t in shooter_tags}
    on_ice_ids = {t.id for t in on_ice_tags}
    participating_ids = {t.id for t in participating_tags}
    unique_tags: dict[int, PlayerStatsTag] = {}

    for t in shooter_tags:
        unique_tags[t.id] = t
    
    for t in on_ice_tags:
        unique_tags[t.id] = t
    
    for t in participating_tags:
        unique_tags[t.id] = t
    
    result = []
    
    for tag_id, tag in unique_tags.items():
        game = tag.game
        ice_zone, net_zone = get_zone_names(tag)
        result.append(
            PlayerTagData(
                id=tag.id,
                game_id=game.id,
                date=str(game.date),
                opponent=game.opponent,
                home=game.home,
                strengths=tag.strengths or "ES",
                ice_x=tag.ice_x,
                ice_y=tag.ice_y,
                ice_zone=ice_zone,
                net_x=tag.net_x,
                net_y=tag.net_y,
                net_zone=net_zone,
                net_height=tag.net_height,
                net_width=tag.net_width,
                shot_result=tag.shot_result.value.value,
                shot_type=tag.shot_type.value.value if tag.shot_type else "UNKNOWN",
                is_shooter=(tag.id in shooter_ids),
                is_participating=(tag.id in participating_ids),
                is_on_ice=(tag.id in on_ice_ids),
            )
        )
        
    result.sort(key=lambda x: x.date, reverse=True)
    return result
