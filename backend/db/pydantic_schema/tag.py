from pydantic import BaseModel
from db.models import ShotAreaTypes, ShotTypeTypes


class TeamTagSchema(BaseModel):

    game_id: int
    play_result: str
    play_type: str

    v5v5_type: str | None = None
    rush_type1: str | None = None
    rush_type2: str | None = None
    takeaway_type: str | None = None
    takeaway_happ_pahp_type: str | None = None
    takeaway_kapp_kahp_type: str | None = None
    takeaway_papp_hahp_type: str | None = None
    takeaway_jatkopaine_type: str | None = None
    hahp_papp_type: str | None = None
    hahp_papp_taytto_type: str | None = None
    hahp_papp_alapeli_type: str | None = None
    hahp_papp_ylapeli_type: str | None = None
    rebound_type: str | None = None
    faceoff_type: str | None = None
    v5v5_other_type: str | None = None
    pp_type: str | None = None
    pp_faceoff_entry_type: str | None = None
    pp_shot_deflection_low_type1: str | None = None
    pp_shot_deflection_low_type2: str | None = None
    pp_blueline_shot_type: str | None = None
    pp_pressure_brokenplay_type: str | None = None
    pp_other_type: str | None = None
    pp_5vs3_type: str | None = None
    pp_av_yv_type: str | None = None
    ot_type: str | None = None
    v3vs3_type: str | None = None
    ps_type: str | None = None

class Coordinate(BaseModel):
    x: int
    y: int


class Shooter(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    jersey_number: int | None = None
    position: str | None = None

class PlayerTagSchema(BaseModel):
    game_id: int
    shot_result: str
    location: Coordinate
    shotZone: ShotAreaTypes
    net: Coordinate
    netZone: str
    shot_type: ShotTypeTypes
    crossice: bool | None = None
    strengths: str

    shooter: Shooter | None = None
    on_ices: list[int]
    participations: list[int]


class AddTag(BaseModel):
    model_config = {"extra": "forbid"}
    tag: TeamTagSchema | PlayerTagSchema


class TeamStatsTagResponse(BaseModel):
    id: int | None
    succes: bool
    tag: dict


class PlayerStatsTagResponse(BaseModel):
    id: int | None
    succes: bool
