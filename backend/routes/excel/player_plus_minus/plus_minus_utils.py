from sqlalchemy.orm import Session

from db.models import Game, GameInRoster, Player, PlayerStatsTag, PlayerStatsTagOnIce, PlayerStatsTagParticipating, Positions, ShotResultTypes, Team
from routes.excel.player_plus_minus.plus_minus_domain import RESULT_TO_COLUMN_MAP, ParticipationTypes, PlusMinusPlayer, PlusMinusTag, StrengthTypes


def get_column_for_stat(strength: StrengthTypes, participation: ParticipationTypes, result: ShotResultTypes):
    """Get the Excel column letter for a given stat combination."""
    return RESULT_TO_COLUMN_MAP[strength][participation][result]


def strenghts_str_to_enum(strength_str: str) -> StrengthTypes:
    """Convert strength string to StrengthTypes enum."""
    strength_mapping = {strength_type.value: strength_type for strength_type in StrengthTypes}
    strength_enum = strength_mapping[strength_str]
    return strength_enum

def should_skip_tag(tag: PlayerStatsTag) -> bool:
    """Check if a tag should be excluded from plus/minus stats."""
    if tag.strengths not in ["ES", "PP", "PK"]:
        return True  # Skip "Empty net tags"

    if tag.shot_result.value in [ShotResultTypes.SHOT_FOR, ShotResultTypes.SHOT_AGAINST]:
        return True  # Skip shot tags, only process chances and goals

    return False


def format_player_name(player: PlusMinusPlayer, roster_players: list[PlusMinusPlayer]) -> str:
    """
    Formats the player's name as just "LASTNAME" by default.
    If 2 players share the same last name in the given roster,
    format as "LASTNAME F." where F is the first (or multiple if needed) initial.
    """

    players_with_same_lastname: list[PlusMinusPlayer] = []
    for other_player in roster_players:
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


def should_skip_goalie(player: PlusMinusPlayer) -> bool:
    """Check if player is a goalie and should be excluded from stats."""
    return player.position == Positions.GOALIE



def split_game_ids(game_ids: str | None) -> list[int]:
    """Parse comma-separated game IDs string into a list of integers."""
    if not game_ids:
        return []
    selected_ids = [int(game_id) for game_id in game_ids.split(",")]
    return selected_ids


def add_tags_to_players(players: dict[int, PlusMinusPlayer], tags: list[PlayerStatsTagOnIce | PlayerStatsTagParticipating]) -> None:
    """Associate stats tags with their corresponding players."""
    for tag in tags:
        if should_skip_tag(tag.tag):  # Skip if empty net or shot tag (not needed for +/- stats)
            continue
        type_of_tag = ParticipationTypes.ON_ICE if type(tag) == PlayerStatsTagOnIce else ParticipationTypes.PARTICIPATING
        pm_tag = PlusMinusTag(tag.tag.game_id, type_of_tag, strenghts_str_to_enum(tag.tag.strengths), tag.tag.shot_result.value)
        players[tag.player_id].add_tag(tag.tag.game_id, pm_tag)


def get_players_in_game(game: Game, players: dict[int, PlusMinusPlayer]) -> list[PlusMinusPlayer]:
    """Get all players who participated in a specific game, sorted by last name."""
    plr_ids = [roster_spot.player_id for roster_spot in game.in_rosters]
    players_in_game: list[PlusMinusPlayer] = []
    for plr_id in plr_ids:
        players_in_game.append(players[plr_id])

    players_in_game.sort(key=lambda p: p.last_name)
    return players_in_game
