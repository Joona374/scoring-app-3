from sqlalchemy.orm import Session, selectinload

from db.models import Game, GameInRoster, Player, PlayerStatsTag, PlayerStatsTagOnIce, PlayerStatsTagParticipating, Team
from routes.excel.player_plus_minus.plus_minus_utils import ParticipationTypes, PlusMinusPlayer, PlusMinusTag, should_skip_tag, split_game_ids, strenghts_str_to_enum


def get_players_in_games(game_ids_str: str | None, team: Team, db: Session) -> dict[int, PlusMinusPlayer]:
    """Fetch all players who participated in the specified games."""
    if not game_ids_str:
        return {}

    selected_ids = [int(game_id) for game_id in game_ids_str.split(",")]
    players = db.query(Player).join(GameInRoster).filter(GameInRoster.game_id.in_(selected_ids), Player.team_id == team.id).distinct().all()

    plus_minus_players = {player.id: PlusMinusPlayer(player) for player in players}
    return plus_minus_players


def get_participating_tags(game_ids_str: str | None, db: Session) -> list[PlayerStatsTagOnIce | PlayerStatsTagParticipating]:
    """Retrieve all on-ice and participating stats tags for the specified games."""
    game_ids = split_game_ids(game_ids_str)
    oi_tags = (
        db.query(PlayerStatsTagOnIce)
        .join(PlayerStatsTagOnIce.tag)
        .options(selectinload(PlayerStatsTagOnIce.tag).selectinload(PlayerStatsTag.shot_result))
        .filter(PlayerStatsTag.game_id.in_(game_ids))
        .all()
    )
    p_tags = (
        db.query(PlayerStatsTagParticipating)
        .join(PlayerStatsTagParticipating.tag)
        .options(selectinload(PlayerStatsTagParticipating.tag).selectinload(PlayerStatsTag.shot_result))
        .filter(PlayerStatsTag.game_id.in_(game_ids))
        .all()
    )
    return oi_tags + p_tags


def add_tags_to_players(players: dict[int, PlusMinusPlayer], tags: list[PlayerStatsTagOnIce | PlayerStatsTagParticipating]) -> None:
    """Associate stats tags with their corresponding players."""
    for tag in tags:
        if should_skip_tag(tag.tag):  # Skip if empty net or shot tag (not needed for +/- stats)
            continue
        type_of_tag = ParticipationTypes.ON_ICE if type(tag) == PlayerStatsTagOnIce else ParticipationTypes.PARTICIPATING
        pm_tag = PlusMinusTag(tag.tag.game_id, type_of_tag, strenghts_str_to_enum(tag.tag.strengths), tag.tag.shot_result.value)
        players[tag.player_id].add_tag(tag.tag.game_id, pm_tag)


def get_players_with_stats(game_ids: str, team: Team, db_session: Session) -> dict[int, PlusMinusPlayer]:
    """Load players and their associated plus/minus stats for the specified games."""
    players: dict[int, PlusMinusPlayer] = get_players_in_games(game_ids, team, db_session)
    tags = get_participating_tags(game_ids, db_session)
    add_tags_to_players(players, tags)

    return players


def get_games_with_rosters(game_ids_str: str, team: Team, db: Session):
    """Fetch game objects with rosters for the specified game IDs."""
    db_query = db.query(Game).options(selectinload(Game.in_rosters)).filter(Game.team_id == team.id)

    if game_ids_str:
        selected_ids = [int(game_id) for game_id in game_ids_str.split(",")]
        db_query = db_query.filter(Game.id.in_(selected_ids))

    games = db_query.all()
    return games
