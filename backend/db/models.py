from sqlalchemy import String, ForeignKey, Enum as SQLEnum, func, DateTime, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List
from enum import Enum

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())


# USER
class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(String(60), unique=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    password_hash: Mapped[str] = mapped_column(String(128))
    has_creation_privilege: Mapped[bool] = mapped_column(default=False)

    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id", name="fk_user_team"), default=None)
    team: Mapped[Optional["Team"]] = relationship(back_populates="users", foreign_keys=[team_id])    

    created_teams: Mapped[List["Team"]] = relationship(back_populates="creator", foreign_keys="Team.creator_id")

class Team(Base):
    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)

    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_team_creator"), nullable=False)
    creator: Mapped["User"] = relationship(back_populates="created_teams", foreign_keys=[creator_id])

    users: Mapped[List["User"]] = relationship(back_populates="team", foreign_keys="User.team_id")
    code: Mapped[List["RegCode"]] = relationship(back_populates="team_related", foreign_keys="RegCode.team_related_id")
    players: Mapped[List["Player"]] = relationship(back_populates="team", foreign_keys="Player.team_id")
    games: Mapped[List["Game"]] = relationship(back_populates="team", foreign_keys="Game.team_id")

class RegCode(Base):
    __tablename__ = "reg_codes"

    code: Mapped[str] = mapped_column(String(6), unique=True, nullable=False)
    creation_code: Mapped[bool] = mapped_column(default=False)
    join_code: Mapped[bool] = mapped_column(default=False)

    team_related_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=True)
    team_related: Mapped[Optional["Team"]] = relationship(back_populates="code", foreign_keys=[team_related_id])


# PLAYER
class Positions(Enum):
    FORWARD = "Hyökkääjä"
    DEFENDER = "Puolustaja"
    GOALIE = "Maalivahti"
   
class Player(Base):
    __tablename__ = "players"

    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    jersey_number: Mapped[int] = mapped_column(nullable=False)
    position: Mapped[Positions] = mapped_column(SQLEnum(Positions), nullable=False)


    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=True)
    team: Mapped["Team"] = relationship(back_populates="players", foreign_keys=[team_id])

    in_rosters: Mapped[List["GameInRoster"]] = relationship(back_populates="player", foreign_keys="GameInRoster.player_id")
    shooter_in: Mapped[List["PlayerStatsTag"]] = relationship(back_populates="shooter", foreign_keys="PlayerStatsTag.shooter_id")
    on_ice_for: Mapped[List["PlayerStatsTagOnIce"]] = relationship(back_populates="player", foreign_keys="PlayerStatsTagOnIce.player_id")
    participating_on: Mapped[List["PlayerStatsTagParticipating"]] = relationship(back_populates="player", foreign_keys="PlayerStatsTagParticipating.player_id")
    

# TYPES
class ShotResultTypes(Enum):
    GOAL_FOR = "Maali +"
    GOAL_AGAINST = "Maali -"
    CHANCE_FOR = "MP +"
    CHANCE_AGAINST = "MP -" 

    @classmethod
    def from_string(cls, str_value: str):
        for item in cls:
            if item.value == str_value:
                return item
        raise ValueError(f"No {cls.__name__} with value '{str_value}'")

class ShotResult(Base):
    __tablename__ = "shot_results"

    value: Mapped[ShotResultTypes] = mapped_column(SQLEnum(ShotResultTypes), nullable=False, unique=True)
    tags: Mapped[List["PlayerStatsTag"]] = relationship(back_populates="shot_result", foreign_keys="PlayerStatsTag.shot_result_id")

class ShotTypeTypes(Enum):
    CARRY_SHOT = "Kuljetuksesta"
    CAN_SHOT = "Catch and release"
    ONE_TIMER = "Onetimer"
    LOWHIGH_SHOT = "Pystysyötöstä"
    TAKEAWAY_SHOT = "Riistosta"
    REBOUND_SHOT = "Rebound"
    DEFLECTION_SHOT = "Ohjaus"


    @classmethod
    def from_string(cls, str_value: str):
        for item in cls:
            if item.value == str_value:
                return item
        raise ValueError(f"No {cls.__name__} with value '{str_value}'")

class ShotType(Base):
    __tablename__ = "shot_types"

    value: Mapped[ShotTypeTypes] = mapped_column(SQLEnum(ShotTypeTypes), nullable=False, unique=True)
    tags: Mapped[List["PlayerStatsTag"]] = relationship(back_populates="shot_type", foreign_keys="PlayerStatsTag.shot_type_id")

class ShotAreaTypes(Enum):
    ZONE_1 = "ZONE_1"
    ZONE_2_MIDDLE = "ZONE_2_MIDDLE"
    ZONE_2_SIDE = "ZONE_2_SIDE"
    HIGH_SLOT = "HIGH_SLOT"
    BLUELINE = "BLUELINE"
    ZONE_4 = "ZONE_4"
    OUTSIDE_FAR = "OUTSIDE_FAR"
    OUTSIDE_CLOSE = "OUTSIDE_CLOSE"
    MISC = "MISC" 

    @classmethod
    def from_string(cls, str_value: str):
        for item in cls:
            if item.value == str_value:
                return item
        raise ValueError(f"No {cls.__name__} with value '{str_value}'")


class ShotArea(Base):
    __tablename__ = "shot_areas"

    value: Mapped[ShotAreaTypes] = mapped_column(SQLEnum(ShotAreaTypes), nullable=False, unique=True)
    tags: Mapped[List["PlayerStatsTag"]] = relationship(back_populates="shot_area", foreign_keys="PlayerStatsTag.shot_area_id")

# GAMES
class Game(Base):
    __tablename__ = "games"

    date: Mapped[Date] = mapped_column(Date, nullable=False)
    opponent: Mapped[str] = mapped_column(String(128), nullable=False)
    home: Mapped[bool] = mapped_column(nullable=False)
    in_rosters: Mapped[List["GameInRoster"]] = relationship(back_populates="game", foreign_keys="GameInRoster.game_id")
    team_stats_tags: Mapped[List["TeamStatsTag"]] = relationship(back_populates="game", foreign_keys="TeamStatsTag.game_id")
    player_stats_tags: Mapped[List["PlayerStatsTag"]] = relationship(back_populates="game", foreign_keys="PlayerStatsTag.game_id")


    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    team: Mapped["Team"] = relationship(back_populates="games", foreign_keys=[team_id])

class GameInRoster(Base):
    __tablename__ = "games_in_roster"

    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    game: Mapped["Game"] = relationship(back_populates="in_rosters", foreign_keys=[game_id])

    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False) 
    player: Mapped[Player] = relationship(back_populates="in_rosters", foreign_keys=[player_id])

    line: Mapped[int] = mapped_column(nullable=False)
    position: Mapped[str] = mapped_column(String(2), nullable=False)


# STATS
class TeamStatsTag(Base):
    __tablename__ = "team_stats_tags"

    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    game: Mapped["Game"] = relationship(back_populates="team_stats_tags", foreign_keys=[game_id])

    play_result: Mapped[str] = mapped_column(String(40), nullable=False)
    play_type: Mapped[str] = mapped_column(String(40), nullable=False)
    v5v5_type: Mapped[str] = mapped_column(String(40), nullable=True)
    rush_type1: Mapped[str] = mapped_column(String(40), nullable=True)
    rush_type2: Mapped[str] = mapped_column(String(40), nullable=True)
    takeaway_type: Mapped[str] = mapped_column(String(40), nullable=True)
    takeaway_happ_pahp_type: Mapped[str] = mapped_column(String(40), nullable=True)
    takeaway_kapp_kahp_type: Mapped[str] = mapped_column(String(40), nullable=True)
    takeaway_papp_hahp_type: Mapped[str] = mapped_column(String(40), nullable=True)
    takeaway_jatkopaine_type: Mapped[str] = mapped_column(String(40), nullable=True)
    hahp_papp_type: Mapped[str] = mapped_column(String(40), nullable=True)
    hahp_papp_taytto_type: Mapped[str] = mapped_column(String(40), nullable=True)
    hahp_papp_alapeli_type: Mapped[str] = mapped_column(String(40), nullable=True)
    hahp_papp_ylapeli_type: Mapped[str] = mapped_column(String(40), nullable=True)
    rebound_type: Mapped[str] = mapped_column(String(40), nullable=True)
    faceoff_type: Mapped[str] = mapped_column(String(40), nullable=True)
    v5v5_other_type: Mapped[str] = mapped_column(String(40), nullable=True)
    pp_type: Mapped[str] = mapped_column(String(40), nullable=True)
    pp_faceoff_entry_type: Mapped[str] = mapped_column(String(40), nullable=True)
    pp_shot_deflection_low_type1: Mapped[str] = mapped_column(String(40), nullable=True)
    pp_shot_deflection_low_type2: Mapped[str] = mapped_column(String(40), nullable=True)
    pp_blueline_shot_type: Mapped[str] = mapped_column(String(40), nullable=True)
    pp_pressure_brokenplay_type: Mapped[str] = mapped_column(String(40), nullable=True)
    pp_other_type: Mapped[str] = mapped_column(String(40), nullable=True)
    pp_5vs3_type: Mapped[str] = mapped_column(String(40), nullable=True)
    pp_av_yv_type: Mapped[str] = mapped_column(String(40), nullable=True)
    ot_type: Mapped[str] = mapped_column(String(40), nullable=True)
    v3vs3_type: Mapped[str] = mapped_column(String(40), nullable=True)
    ps_type: Mapped[str] = mapped_column(String(40), nullable=True)

    def __repr__(self):
        datapoints = []
        for key, value in vars(self).items():
            if value != None and key != "_sa_instance_state":
                if type(value) == str:
                    datapoint = f"{key}='{value}'"
                else:
                    datapoint = f"{key}={value}"

                datapoints.append(datapoint)

        repr_string = "TeamStasTag("
        for datapoint in datapoints:
            repr_string += f"{datapoint}, "
        repr_string = repr_string[:-2] + ")\n"

        return repr_string
    
class PlayerStatsTag(Base):
    __tablename__ = "player_stats_tags"

    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    game: Mapped["Game"] = relationship(back_populates="player_stats_tags", foreign_keys=[game_id])

    ice_x: Mapped[int] = mapped_column(nullable=False)
    ice_y: Mapped[int] = mapped_column(nullable=False)

    shot_area_id: Mapped[int] = mapped_column(ForeignKey("shot_areas.id"), nullable=False)
    shot_area: Mapped["ShotArea"] = relationship(back_populates="tags", foreign_keys=[shot_area_id])

    net_x: Mapped[int] = mapped_column(nullable=False)
    net_y: Mapped[int] = mapped_column(nullable=False)

    net_height: Mapped[str] = mapped_column(String(40), nullable=False)
    net_width: Mapped[str] = mapped_column(String(40), nullable=False)

    # SHOT RESULT
    shot_result_id: Mapped[int] = mapped_column(ForeignKey("shot_results.id"), nullable=False)
    shot_result: Mapped["ShotResult"] = relationship(back_populates="tags", foreign_keys=[shot_result_id])

    # SHOT TYPE
    shot_type_id: Mapped[int] = mapped_column(ForeignKey("shot_types.id"))
    shot_type: Mapped["ShotType"] = relationship(back_populates="tags", foreign_keys=[shot_type_id])

    shooter_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=True)
    shooter: Mapped["Player"] = relationship(back_populates="shooter_in", foreign_keys=[shooter_id])

    crossice: Mapped[bool] = mapped_column(nullable=True)

    strengths: Mapped[str] = mapped_column(String(3))

    players_on_ice: Mapped[List["PlayerStatsTagOnIce"]] = relationship(back_populates="tag", foreign_keys="PlayerStatsTagOnIce.tag_id")
    players_participating: Mapped[List["PlayerStatsTagParticipating"]] = relationship(back_populates="tag", foreign_keys="PlayerStatsTagParticipating.tag_id")

class PlayerStatsTagOnIce(Base):
    __tablename__ = "player_stats_tag_on_ice"

    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    player: Mapped["Player"] = relationship(back_populates="on_ice_for", foreign_keys=[player_id])

    tag_id: Mapped[int] = mapped_column(ForeignKey("player_stats_tags.id"), nullable=False)
    tag: Mapped["PlayerStatsTag"] = relationship(back_populates="players_on_ice", foreign_keys=[tag_id])

class PlayerStatsTagParticipating(Base):
    __tablename__ = "player_stats_tag_participating"

    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    player: Mapped["Player"] = relationship(back_populates="participating_on", foreign_keys=[player_id])

    tag_id: Mapped[int] = mapped_column(ForeignKey("player_stats_tags.id"), nullable=False)
    tag: Mapped["PlayerStatsTag"] = relationship(back_populates="players_participating", foreign_keys=[tag_id])