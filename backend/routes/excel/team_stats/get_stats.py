from collections import defaultdict
from db.models import Game, TeamStatsTag
from sqlalchemy.orm import Session


def get_team_stats_tags(games: list[Game], db_session: Session) -> list[TeamStatsTag]:
    """
    Retrieves team stats tags for the given list of games from the database.
    Args:
        games (list[Game]): List of Game objects.
        db_session (Session): Database session.
    Returns:
        list[TeamStatsTag]: List of TeamStatsTag objects associated with the games.
    """

    selected_game_ids = [game.id for game in games]
    team_tags = db_session.query(TeamStatsTag).filter(TeamStatsTag.game_id.in_(selected_game_ids)).all()
    return team_tags


def get_games_stats_dict(all_tags: list[TeamStatsTag]) -> defaultdict[int, list[TeamStatsTag]]:
    """
    Groups TeamStatsTag objects by their game_id.
    Args:
        all_tags (list[TeamStatsTag]): List of TeamStatsTag instances.
    Returns:
        defaultdict[int, list[TeamStatsTag]]: Dictionary with game_ids as keys and lists of tags as values.
    """

    games_stats_dict = defaultdict(list)
    for tag in all_tags:
        games_stats_dict[tag.game_id].append(tag)

    return games_stats_dict
