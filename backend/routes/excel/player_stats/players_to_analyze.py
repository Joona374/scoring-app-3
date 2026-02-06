from collections import defaultdict
from sqlalchemy.orm import Session, joinedload

from db.models import Game, PlayerStatsTag, Team
from routes.excel.player_stats.player_stats_utils import PlayerStats
from routes.excel.stats_utils import get_selected_games

def build_players_to_analyze_dict(selected_games: list[Game]) -> defaultdict[int, PlayerStats]:
    """
    Builds a data collecting dictionary that initializes player statistics for analysis.
    This function creates a defaultdict where each key is a player ID (int) and the value is a dictionary
    containing initialized fields for player stats, including first name, last name, game count, and lists
    for tags and stats. It iterates through the provided list of selected games, extracting players from
    their in-rosters, and populates the dictionary with player details and increments the game count for
    each player across the games.
    Args:
        selected_games (list[Game]): A list of Game objects from which to extract player information.
    Returns:
        defaultdict[int, dict]: A defaultdict with player IDs as keys and dictionaries as values,
        each containing keys like 'games' (int), 'first_name' (str), 'last_name' (str), 'shooter_tags' (list),
        'on_ice_tags' (list), 'cell_values' (dict), and 'per_game_stats' (list).
    """

    players_to_analyze: defaultdict[int, PlayerStats] = defaultdict(
        lambda: {"games": 0, "first_name": "", "last_name": "", "shooter_tags": [], "on_ice_tags": [], "cell_values": {}, "per_game_stats": []}
    )

    for game in selected_games:
        for in_roster_object in game.in_rosters:
            player = in_roster_object.player
            if player.id not in players_to_analyze:
                players_to_analyze[player.id]["first_name"] = player.first_name
                players_to_analyze[player.id]["last_name"] = player.last_name

            players_to_analyze[player.id]["games"] += 1

    return players_to_analyze


def get_PSTs_for_games(selected_games: list[Game], db_session: Session):
    """
    Retrieves a list of PlayerStatsTag objects for the specified games, with eager loading of related entities.

    This function performs a database query to fetch PlayerStatsTag records that are associated with the provided list of games.
    It uses joinedload to eagerly load related objects (shooter, game, shot_result, shot_area, shot_type, players_on_ice, and players_participating)
    to avoid N+1 query problems.

    Args:
        db_session (Session): The SQLAlchemy database session used to execute the query.
        selected_games (list[Game]): A list of Game objects to filter the PlayerStatsTag records by their associated game.

    Returns:
        list[PlayerStatsTag]: A list of PlayerStatsTag objects matching the selected games, with related entities eager loaded.
    """

    game_ids = [game.id for game in selected_games]
    player_stats_tags = (
        db_session.query(PlayerStatsTag)
        .options(
            joinedload(PlayerStatsTag.shooter),
            joinedload(PlayerStatsTag.game),
            joinedload(PlayerStatsTag.shot_result),
            joinedload(PlayerStatsTag.shot_area),
            joinedload(PlayerStatsTag.shot_type),
            joinedload(PlayerStatsTag.players_on_ice),
            joinedload(PlayerStatsTag.players_participating),
        )
        .filter(PlayerStatsTag.game_id.in_(game_ids))
        .all()
    )
    return player_stats_tags


def add_players_tags(players_to_analyze: defaultdict[int, PlayerStats], player_stats_tags: list[PlayerStatsTag]) -> None:
    for tag in player_stats_tags:
        # 1. Add the tag to correct players "shooter_tags"
        if tag.shooter:
            players_to_analyze[tag.shooter.id]["shooter_tags"].append(tag)

        # 2. Add the tag to "on_ice_tags" for all players on ice for the chance
        for on_ice_tag in tag.players_on_ice:
            players_to_analyze[on_ice_tag.player_id]["on_ice_tags"].append(tag)


def get_players_to_analyze(game_ids_str: str | None, team: Team, db_session: Session) -> defaultdict[int, PlayerStats]:
    selected_games = get_selected_games(team, game_ids_str)
    player_stats_tags = get_PSTs_for_games(selected_games, db_session)
    players_to_analyze = build_players_to_analyze_dict(selected_games)
    add_players_tags(players_to_analyze, player_stats_tags)  # edits palyers_to_analyze in place

    return players_to_analyze
