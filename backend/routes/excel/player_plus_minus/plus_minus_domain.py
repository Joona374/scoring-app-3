from collections import defaultdict
from enum import Enum
from typing import TypeAlias, TypedDict
from datetime import date as datetime_date

from db.models import Player, Positions, ShotResultTypes

FIRST_DEFENDER_ROW = 4
FIRST_FORWARD_ROW = 26

NAME_COLUMNS = ["G", "U", "AI", "AW"]

SHOTRESULT_TO_CODE_MAP = {
    ShotResultTypes.GOAL_FOR: "G+",
    ShotResultTypes.GOAL_AGAINST: "G-",
    ShotResultTypes.CHANCE_FOR: "C+",
    ShotResultTypes.CHANCE_AGAINST: "C-",
}


class ParticipationTypes(Enum):
    ON_ICE = "on_ice"
    PARTICIPATING = "participating"


class StrengthTypes(Enum):
    EVEN_STRENGTH = "ES"
    POWERPLAY = "PP"
    PENALTY_KILL = "PK"


RESULT_TO_COLUMN_MAP = {
    StrengthTypes.EVEN_STRENGTH: {
        ParticipationTypes.ON_ICE: {
            ShotResultTypes.GOAL_FOR: "A",
            ShotResultTypes.GOAL_AGAINST: "B",
            ShotResultTypes.CHANCE_FOR: "D",
            ShotResultTypes.CHANCE_AGAINST: "E",
        },
        ParticipationTypes.PARTICIPATING: {
            ShotResultTypes.GOAL_FOR: "H",
            ShotResultTypes.GOAL_AGAINST: "I",
            ShotResultTypes.CHANCE_FOR: "K",
            ShotResultTypes.CHANCE_AGAINST: "L",
        },
    },
    StrengthTypes.POWERPLAY: {
        ParticipationTypes.ON_ICE: {
            ShotResultTypes.GOAL_FOR: "O",
            ShotResultTypes.GOAL_AGAINST: "P",
            ShotResultTypes.CHANCE_FOR: "R",
            ShotResultTypes.CHANCE_AGAINST: "S",
        },
        ParticipationTypes.PARTICIPATING: {
            ShotResultTypes.GOAL_FOR: "V",
            ShotResultTypes.GOAL_AGAINST: "W",
            ShotResultTypes.CHANCE_FOR: "Y",
            ShotResultTypes.CHANCE_AGAINST: "Z",
        },
    },
    StrengthTypes.PENALTY_KILL: {
        ParticipationTypes.ON_ICE: {
            ShotResultTypes.GOAL_FOR: "AC",
            ShotResultTypes.GOAL_AGAINST: "AD",
            ShotResultTypes.CHANCE_FOR: "AF",
            ShotResultTypes.CHANCE_AGAINST: "AG",
        },
        ParticipationTypes.PARTICIPATING: {
            ShotResultTypes.GOAL_FOR: "AJ",
            ShotResultTypes.GOAL_AGAINST: "AK",
            ShotResultTypes.CHANCE_FOR: "AM",
            ShotResultTypes.CHANCE_AGAINST: "AN",
        },
    },
}


StatsDict: TypeAlias = dict[StrengthTypes, dict[ParticipationTypes, dict[ShotResultTypes, int]]]


class PlayerData(TypedDict):
    name: str
    position: Positions
    GP: int
    stats: StatsDict


class GameDataStructure(TypedDict):
    game_id: int
    opponent: str
    home: bool
    date: datetime_date
    roster: dict[int, PlayerData]
    roster_by_positions: dict[Positions, list[PlayerData]]


class PlusMinusTag:
    def __init__(self, tag_game_id: int, tag_type: ParticipationTypes, tag_strength: StrengthTypes, tag_gesult: ShotResultTypes):
        """Initialize a plus/minus tag with game context and stat details."""
        self.game_id: int = tag_game_id
        self.type: ParticipationTypes = tag_type
        self.strengths: StrengthTypes = tag_strength
        self.results: ShotResultTypes = tag_gesult

    def __str__(self):
        return f"\nPlusMinusTag(game_id={self.game_id}, type={self.type}, strengths={self.strengths}, results={self.results})"

    def __repr__(self):
        return self.__str__()


class PlusMinusPlayer:
    def __init__(self, player: Player):
        """Initialize a plus/minus player with base player information."""
        self.id: int = player.id
        self.first_name: str = player.first_name
        self.last_name: str = player.last_name
        self.position: Positions = player.position
        self.plusminus_tags: defaultdict[int, list[PlusMinusTag]] = defaultdict(list[PlusMinusTag])  # Key is game id

    def add_tag(self, game_id: int, tag: PlusMinusTag):
        """Add a plus/minus tag to the player for a specific game."""
        self.plusminus_tags[game_id].append(tag)

    def get_tags_for_game(self, game_id) -> list[PlusMinusTag]:
        """Get all plus/minus tags for a specific game."""
        return self.plusminus_tags[game_id]


    def _build_empty_stats_dict(self) -> StatsDict:
        """
        Builds an empty statistics dictionary with nested keys for strength, participation type, and shot result, all initialized to 0.
        """

        empty_stats: StatsDict = {}

        for strenght in StrengthTypes:
            empty_stats[strenght] = {}

            for participation_type in ParticipationTypes:
                empty_stats[strenght][participation_type] = {}

                for result in ShotResultTypes:
                    if result in [ShotResultTypes.SHOT_AGAINST, ShotResultTypes.SHOT_FOR]:
                        continue  # Skip shots

                    empty_stats[strenght][participation_type][result] = 0

        return empty_stats

    def get_game_stats(self, game_id) -> StatsDict:
        """Calculate plus/minus stats for a specific game."""
        stats_dict = self._build_empty_stats_dict()

        if game_id not in self.plusminus_tags:
            return stats_dict

        for tag in self.plusminus_tags[game_id]:
            stats_dict[tag.strengths][tag.type][tag.results] += 1

        return stats_dict

    def get_total_stats(self) -> StatsDict:
        """Calculate aggregated plus/minus stats across all games."""
        total_dict = self._build_empty_stats_dict()

        for _, tags in self.plusminus_tags.items():
            for tag in tags:
                total_dict[tag.strengths][tag.type][tag.results] += 1

        return total_dict

    def get_games_played(self) -> int:
        """Get the number of games the player has participated in."""
        return len(self.plusminus_tags)

    def __str__(self):
        return f"PlusMinusPlayer(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}', position={self.position}, plusminus_tags=\n{dict(self.plusminus_tags)})"
