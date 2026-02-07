# routes/analysis.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from db.db_manager import get_db_session
from db.models import PlayerStatsTag, Game, User, ShotType, ShotResultTypes
from utils import (
    get_current_user_id, to_label, side_of_enum, is_goal_enum,
    allow_result_enum, parse_shot_type_values, is_chance_enum, is_shot_enum
)

router = APIRouter(prefix="/analysis", tags=["analysis"])

class HeatPoint(BaseModel):
    x: int; y: int; weight: float
    result: str; side: str; is_goal: bool; area: str

class NetBinCount(BaseModel):
    zone: str; count: int

class AnalysisResponse(BaseModel):
    game_ids: list[int]
    totals: dict
    by_result: dict[str, int]
    by_type: dict[str, int]
    by_strengths: dict[str, int]
    by_area: dict[str, int]
    crossice: dict[str, int]
    ice_points: list[HeatPoint]
    net_points: list[HeatPoint]
    net_bins: list[NetBinCount]

@router.get("", response_model=AnalysisResponse)
def get_analysis(
    game_ids: str = Query(...),
    shooter_ids: Optional[str] = Query(None),
    strengths: Optional[str] = Query(None),
    shot_types: Optional[str] = Query(None),
    show_cf: bool = Query(True),
    show_ca: bool = Query(True),
    show_gf: bool = Query(True),
    show_ga: bool = Query(True),
    show_sf: bool = Query(True),   # NEW
    show_sa: bool = Query(True),   # NEW
    db: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
):
    # parse CSVs
    gid_list = [int(x) for x in game_ids.split(",") if x.strip().isdigit()]
    shooter_list = [int(x) for x in (shooter_ids or "").split(",") if x.strip().isdigit()]
    strengths_list = [x.strip() for x in (strengths or "").split(",") if x.strip()]
    shot_types_list = [x.strip() for x in (shot_types or "").split(",") if x.strip()]

    if not gid_list:
        raise HTTPException(400, "Provide at least one game_id")

    # permission check
    user = db.query(User).filter(User.id == current_user_id).first()
    games = db.query(Game).filter(Game.id.in_(gid_list)).all()
    if len(games) != len(gid_list): raise HTTPException(404, "One or more games not found")
    for g in games:
        if g.team != user.team: raise HTTPException(401, "No permission for one or more games")

    # base query
    q = db.query(PlayerStatsTag).filter(PlayerStatsTag.game_id.in_(gid_list))
    if shooter_list:
        q = q.filter(PlayerStatsTag.shooter_id.in_(shooter_list))
    if strengths_list:
        q = q.filter(PlayerStatsTag.strengths.in_(strengths_list))
    if shot_types_list:
        enum_vals = parse_shot_type_values(shot_types_list)
        if enum_vals:
            q = q.join(PlayerStatsTag.shot_type, isouter=True).filter(ShotType.value.in_(enum_vals))

    tags = q.all()

    # filter by result type using enums
    tags = [
        t for t in tags
        if t.shot_result and allow_result_enum(
            t.shot_result.value, show_gf, show_ga, show_cf, show_ca, show_sf, show_sa
        )
    ]

    # after tags filtering
    events_total = len(tags)
    goals = sum(1 for t in tags if is_goal_enum(t.shot_result.value))
    maalipaikat = sum(1 for t in tags if is_chance_enum(t.shot_result.value))
    laukaukset = sum(1 for t in tags if is_shot_enum(t.shot_result.value))

    # keep your existing behavior for Sh% (goals / all returned events)
    shooting_pct = round((goals / events_total) * 100, 1) if events_total else 0.0


    def inc(d: dict, key: Optional[str]):
        key = key if key is not None else "NONE"
        d[key] = d.get(key, 0) + 1

    by_result: dict[str,int] = {}
    by_type: dict[str,int] = {}
    by_strengths: dict[str,int] = {}
    by_area: dict[str,int] = {}
    crossice = {"true": 0, "false": 0, "none": 0}
    ice_points, net_points = [], []
    net_bins = {}

    for t in tags:
        res_enum: ShotResultTypes = t.shot_result.value
        res_label = to_label(res_enum) or ""
        stype_label = to_label(t.shot_type.value) if t.shot_type else None
        area_label = to_label(t.shot_area.value) if t.shot_area else None

        inc(by_result, res_label)
        inc(by_type, stype_label)
        inc(by_strengths, t.strengths)
        inc(by_area, area_label)

        if t.crossice is True: crossice["true"] += 1
        elif t.crossice is False: crossice["false"] += 1
        else: crossice["none"] += 1

        side = side_of_enum(res_enum)
        goal = is_goal_enum(res_enum)

        ice_points.append({
            "x": t.ice_x, "y": t.ice_y, "weight": 1.0,
            "result": res_label, "side": side, "is_goal": goal, "area": area_label or ""
        })
        net_points.append({
            "x": t.net_x, "y": t.net_y, "weight": 1.0,
            "result": res_label, "side": side, "is_goal": goal, "area": area_label or ""
        })

        zone = f"{t.net_height}-{t.net_width}"
        net_bins[zone] = net_bins.get(zone, 0) + 1

    return {
        "game_ids": gid_list,
        "totals": {
            # new explicit buckets
            "shots": laukaukset,
            "chances": maalipaikat,
            "goals": goals,
            "shooting_pct": shooting_pct,
        },
        "by_result": by_result,
        "by_type": by_type,
        "by_strengths": by_strengths,
        "by_area": by_area,
        "crossice": crossice,
        "ice_points": ice_points,
        "net_points": net_points,
        "net_bins": [{"zone": k, "count": v} for k, v in sorted(net_bins.items())],
    }
