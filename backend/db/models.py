from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List

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

    # This is a foreign key to Team
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id", name="fk_user_team"))
    team: Mapped[Optional["Team"]] = relationship(back_populates="users", foreign_keys=[team_id])

    created_teams: Mapped[List["Team"]] = relationship(back_populates="creator", foreign_keys="Team.creator_id")

class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(6), unique=False, nullable=False)

    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_team_creator"), nullable=False)
    creator: Mapped["User"] = relationship(back_populates="created_teams", foreign_keys=[creator_id])

    #This is foreign key to User
    users: Mapped[List["User"]] = relationship(back_populates="team", foreign_keys="User.team_id")
