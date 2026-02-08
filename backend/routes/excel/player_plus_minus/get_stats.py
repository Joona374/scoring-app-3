from collections import defaultdict
import copy

from sqlalchemy.orm import Session, joinedload

from routes.excel.player_plus_minus.constants import EMPTY_STATS, SHOTRESULT_TO_CODE_MAP, GameDataStructure, PlayerData
from db.models import Player, GameInRoster, Game, PlayerStatsTag, PlayerStatsTagOnIce, PlayerStatsTagParticipating, ShotResultTypes


def format_player_name(player: Player, in_rosters: list[GameInRoster]) -> str:
    """
    Formats the player's name as just "LASTNAME" by default.
    If 2 players share the same last name in the given roster,
    format as "LASTNAME F." where F is the first (or multiple if needed) initial.
    """

    players_with_same_lastname = []
    for roster_spot in in_rosters:
        other_player = roster_spot.player
        if other_player.last_name == player.last_name and other_player.id != player.id:
            players_with_same_lastname.append(other_player)

    if not players_with_same_lastname:
        return f"{player.last_name.upper()}"

    initials = player.first_name[0]
    for other_player in players_with_same_lastname:
        for i in range(0, len(other_player.first_name)):
            if initials[i] == other_player.first_name[i]:
                initials += player.first_name[i + 1]
            else:
                break
    return f"{player.last_name.upper()} {initials}."


def build_roster_dict(game: Game) -> dict[int, PlayerData]:
    """
    Builds a dictionary mapping player IDs to their data (name, position, empty stats) from the game's rosters.
    Args:
        game (Game): The game object containing rosters.
    Returns:
        dict[int, PlayerData]: Dictionary with player IDs as keys and PlayerData as values.
    """

    roster_dict: dict[int, PlayerData] = {}

    for roster_spot in game.in_rosters:
        player = roster_spot.player
        roster_dict[player.id] = {"name": format_player_name(player, game.in_rosters),
                                  "position": player.position.name,
                                  "GP": 0,
                                  "stats": EMPTY_STATS.copy()}

    return roster_dict

def build_game_data_structure(game: Game) -> GameDataStructure:
    """
    Builds a game data structure from a Game object.
    Args:
        game (Game): The game object to process.
    Returns:
        GameDataStructure: A dictionary containing game details and roster.
    """

    game_roster = build_roster_dict(game)
    data_structure: GameDataStructure = {"game_id": game.id, 
                                         "opponent": game.opponent, 
                                         "home": game.home, 
                                         "date": game.date, 
                                         "roster": game_roster,
                                         "roster_by_positions": {}}

    return data_structure


def convert_roster_to_lists_by_position(roster: dict) -> dict:
    listed_roster = {"forwards": [], "defenders": []}

    for player_dict in roster.values():
        if player_dict["position"] == "FORWARD":
            listed_roster["forwards"].append(player_dict)
        elif player_dict["position"] == "DEFENDER":
            listed_roster["defenders"].append(player_dict)

    for group in listed_roster.values():
        group.sort(key=lambda player: player["name"])

    return listed_roster

def get_player_stats_tags_for_games(games: list[Game], db_session: Session):
    game_ids = [game.id for game in games]

    player_stats_tags = (
        db_session.query(PlayerStatsTag)
        .options(
            joinedload(PlayerStatsTag.shot_result),
            joinedload(PlayerStatsTag.players_on_ice).joinedload(PlayerStatsTagOnIce.player),
            joinedload(PlayerStatsTag.players_participating).joinedload(PlayerStatsTagParticipating.player),
        )
        .filter(PlayerStatsTag.game_id.in_(game_ids))
        .all()
    )

    return player_stats_tags

def get_on_ice_tags_for_games(games: list[Game], db_session: Session) -> defaultdict[int, list[PlayerStatsTagOnIce]]:
    """
    Retrieves on-ice tags for a list of games and groups them by player stats tag ID.
    Args:
        games (list[Game]): List of Game objects to query tags for.
        db_session (Session): Database session for querying.
    Returns:
        defaultdict(list): Dictionary with PlayerStatsTag IDs as keys and lists of PlayerStatsTagOnIce objects as values.
    """
    game_ids = [game.id for game in games]

    on_ice_tags = db_session.query(PlayerStatsTagOnIce).join(PlayerStatsTag).filter(PlayerStatsTag.game_id.in_(game_ids)).all()
    on_ice_tags_by_PST_id = defaultdict(list)
    for on_ice_tag in on_ice_tags:
        on_ice_tags_by_PST_id[on_ice_tag.tag_id].append(on_ice_tag)

    return on_ice_tags_by_PST_id

def get_participating_tags_for_games(games: list[Game], db_session: Session) -> defaultdict[int, list[PlayerStatsTagParticipating]]:
    """
    Retrieves participation tags for a list of games and groups them by player stats tag ID.
    Args:
        games (list[Game]): List of Game objects to query tags for.
        db_session (Session): Database session for querying.
    Returns:
        defaultdict(list): Dictionary with PlayerStatsTag IDs as keys and lists of PlayerStatsTagParticipating objects as values.
    """
    game_ids = [game.id for game in games]

    participating_tags = db_session.query(PlayerStatsTagParticipating).join(PlayerStatsTag).filter(PlayerStatsTag.game_id.in_(game_ids)).all()
    participating_tags_by_PST_id = defaultdict(list)
    for partic_link in participating_tags:
        participating_tags_by_PST_id[partic_link.tag_id].append(partic_link)

    return participating_tags_by_PST_id

def group_tags_by_game(player_stats_tags: list[PlayerStatsTag]) -> defaultdict[int, list[PlayerStatsTag]]:
    """
    Groups player stats tags by their game ID.
    Args:
        player_stats_tags (list[PlayerStatsTag]): List of PlayerStatsTag objects to group.
    Returns:
        defaultdict[int, list[PlayerStatsTag]]: Dictionary with game IDs as keys and lists of tags as values.
    """
    
    tag_container = defaultdict(list)
    for tag in player_stats_tags:
        tag_container[tag.game_id].append(tag)
    
    return tag_container

def add_new_players_to_total_stats(game_data: GameDataStructure, total_stats: dict):
    # Iterate over each player in the roster
    for id, player_data in game_data["roster"].items():

        # If the player (id) is not already in the total_stats dict, copy this games data as the first game and update GP to 1
        if id not in total_stats:
            total_data = copy.deepcopy(player_data)
            total_data["GP"] = 1
            total_stats[id] = total_data

        # if player (id) already in the total_stats, just update the games played
        else:
            total_stats[id]["GP"] += 1

def should_skip_tag(tag: PlayerStatsTag) -> bool:
    if tag.strengths not in ["ES", "PP", "PK"]:
        return True  # Skip "Empty net tags"

    if tag.shot_result.value in [ShotResultTypes.SHOT_FOR, ShotResultTypes.SHOT_AGAINST]:
        return True  # Skip shot tags, only process chances and goals

    return False


def handle_player_stats_tag(
    tag: PlayerStatsTag,
    on_ice_tags: defaultdict[int, list[PlayerStatsTagOnIce]],
    participating_tags: defaultdict[int, list[PlayerStatsTagParticipating]],
    game_data: GameDataStructure,
    total_stats: dict[int, PlayerData],
):
    """
    Handles player statistics for a given tag by updating on-ice and participating player stats in game_data and total_stats.
    Parameters:
    - tag (PlayerStatsTag): The player stats tag to process.
    - on_ice_tags (defaultdict[int, list[PlayerStatsTagOnIce]]): Mapping of tag IDs to on-ice tags.
    - participating_tags (defaultdict[int, list[PlayerStatsTagParticipating]]): Mapping of tag IDs to participating tags.
    - game_data (GameDataStructure): The game data structure to update.
    - total_stats (dict[int, PlayerData]): Total stats dictionary to update.
    """
    ############################################################################
    # TODO: Figure out better way to map these.
    # Use some models etc instead of these weird parsed strings to track tags.
    strengths = tag.strengths
    result_part = SHOTRESULT_TO_CODE_MAP[tag.shot_result.value]

    tags_on_ice = on_ice_tags[tag.id]
    OI_player_ids = [tag.player.id for tag in tags_on_ice]
    for id in OI_player_ids:
        game_data["roster"][id]["stats"][f"{strengths}-OI{result_part}"] += 1
        total_stats[id]["stats"][f"{strengths}-OI{result_part}"] += 1

    tags_participating = participating_tags[tag.id]
    P_player_ids = [tag.player.id for tag in tags_participating]
    for id in P_player_ids:
        game_data["roster"][id]["stats"][f"{strengths}-P{result_part}"] += 1
        total_stats[id]["stats"][f"{strengths}-P{result_part}"] += 1
    ############################################################################


def get_plusminus_games_data(games: list[Game], db_session: Session) -> tuple[list[GameDataStructure], dict[int, PlayerData]]:
    game_stats: list[GameDataStructure] = []
    total_stats: dict[int, PlayerData] = {}

    tags_for_games = get_player_stats_tags_for_games(games, db_session)
    player_stats_tags_by_game_id = group_tags_by_game(tags_for_games)
    on_ice_tags_by_player_stats_tag_id = get_on_ice_tags_for_games(games, db_session)
    participating_tags_by_player_stats_tag_id = get_participating_tags_for_games(games, db_session)

    for game in games:
        game_data = build_game_data_structure(game)
        add_new_players_to_total_stats(game_data, total_stats) # Edits total_stats in place, by adding new players, and updating Games PLayed for before seen players

        tags = player_stats_tags_by_game_id[game.id]
        for tag in tags:
            if should_skip_tag(tag): # Skip ff empty-net tag or just a shot (not goal or scoring chance) 
                continue
            handle_player_stats_tag(tag, on_ice_tags_by_player_stats_tag_id, participating_tags_by_player_stats_tag_id, game_data, total_stats)

        game_data["roster_by_positions"] = convert_roster_to_lists_by_position(game_data["roster"])

        game_stats.append(game_data)

    game_stats.sort(key=lambda game: game["date"], reverse=True)
    listed_total_data = convert_roster_to_lists_by_position(total_stats)
    return game_stats, listed_total_data
