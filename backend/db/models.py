from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List
from enum import Enum

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
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

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)

    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_team_creator"), nullable=False)
    creator: Mapped["User"] = relationship(back_populates="created_teams", foreign_keys=[creator_id])

    users: Mapped[List["User"]] = relationship(back_populates="team", foreign_keys="User.team_id")
    code: Mapped[List["RegCode"]] = relationship(back_populates="team_related", foreign_keys="RegCode.team_related_id")
    players: Mapped[List["Player"]] = relationship(back_populates="team", foreign_keys="Team.team_id")


class RegCode(Base):
    __tablename__ = "reg_codes"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
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

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    position: Mapped[Positions] = mapped_column(SQLEnum(Positions), nullable=False)

    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=True)
    team: Mapped["Team"] = relationship(back_populates="players", foreign_keys=[team_id])