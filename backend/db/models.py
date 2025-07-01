from sqlalchemy import String, ForeignKey, Enum as SQLEnum, func, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List
from enum import Enum

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())


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


class RegCode(Base):
    __tablename__ = "reg_codes"

    code: Mapped[str] = mapped_column(String(6), unique=True, nullable=False)
    creation_code: Mapped[bool] = mapped_column(default=False)
    join_code: Mapped[bool] = mapped_column(default=False)

    team_related_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=True)
    team_related: Mapped[Optional["Team"]] = relationship(back_populates="code", foreign_keys=[team_related_id])


class Positions(Enum):
    FORWARD = "Hyökkääjä"
    DEFENDER = "Puolustaja"
    GOALIE = "Maalivahti"
   

class Player(Base):
    __tablename__ = "players"

    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    position: Mapped[Positions] = mapped_column(SQLEnum(Positions), nullable=False)

    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=True)
    team: Mapped["Team"] = relationship(back_populates="players", foreign_keys=[team_id])

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
    tags: Mapped[List["Tag"]] = relationship(back_populates="shot_result", foreign_keys="Tag.shot_result_id")

class ShotTypeTypes(Enum):
    WRIST_SHOT = "Wrist Shot"
    SLAP_SHOT = "Slap Shot"
    SNAP_SHOT = "Snap Shot"
    ONE_TIMER = "One-Timer"

    @classmethod
    def from_string(cls, str_value: str):
        for item in cls:
            if item.value == str_value:
                return item
        raise ValueError(f"No {cls.__name__} with value '{str_value}'")

class ShotType(Base):
    __tablename__ = "shot_types"

    value: Mapped[ShotTypeTypes] = mapped_column(SQLEnum(ShotTypeTypes), nullable=False, unique=True)
    tags: Mapped[List["Tag"]] = relationship(back_populates="shot_type", foreign_keys="Tag.shot_type_id")

class Tag(Base):
    __tablename__ = "tags"

    ice_x: Mapped[int] = mapped_column(nullable=False)
    ice_y: Mapped[int] = mapped_column(nullable=False)

    # SHOT RESULT
    shot_result_id: Mapped[int] = mapped_column(ForeignKey("shot_results.id"), nullable=False)
    shot_result: Mapped["ShotResult"] = relationship(back_populates="tags", foreign_keys=[shot_result_id])

    # SHOT TYPE
    shot_type_id: Mapped[int] = mapped_column(ForeignKey("shot_types.id"))
    shot_type: Mapped["ShotType"] = relationship(back_populates="tags", foreign_keys=[shot_type_id])
