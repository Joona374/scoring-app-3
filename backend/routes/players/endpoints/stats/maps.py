from collections import defaultdict
from db.models import PlayerStatsTag, ShotResultTypes
from db.pydantic_schema.shared import ZoneData
from db.pydantic_schema.player_page import MarkerData


def get_zone_names(tag: PlayerStatsTag) -> tuple[str, str]:
    ice_zone_name = tag.shot_area.value.value if tag.shot_area else "UNKNOWN"
    if ice_zone_name in ["ZONE_2_SIDE", "ZONE_4", "OUTSIDE_FAR", "OUTSIDE_CLOSE"]:
        side = "_LEFT" if tag.ice_x < 50 else "_RIGHT"
        ice_zone_name += side
    net_zone_name = f"{tag.net_height}-{tag.net_width}"
    return ice_zone_name, net_zone_name

def should_skip_tag(tag: PlayerStatsTag) -> bool:
    result = tag.shot_result.value
    if result not in [ShotResultTypes.GOAL_FOR, ShotResultTypes.CHANCE_FOR]:
        return True
    return False

def add_markers(tag: PlayerStatsTag, ice_markers: list[MarkerData], net_markers: list[MarkerData]) -> None:
    result = tag.shot_result.value
    ice_markers.append(MarkerData(x=tag.ice_x, y=tag.ice_y, result=result.value))
    net_markers.append(MarkerData(x=tag.net_x, y=tag.net_y, result=result.value))

def increment_zone_data(tag: PlayerStatsTag, ice_zones: defaultdict[str, ZoneData], net_zones: defaultdict[str, ZoneData]) -> None:
    result = tag.shot_result.value
    ice_zone_name, net_zone_name = get_zone_names(tag)

    if result == ShotResultTypes.GOAL_FOR:
        ice_zones[ice_zone_name].goals_for += 1
        ice_zones[ice_zone_name].chances_for += 1
        net_zones[net_zone_name].goals_for += 1
        net_zones[net_zone_name].chances_for += 1

    elif result == ShotResultTypes.CHANCE_FOR:
        ice_zones[ice_zone_name].chances_for += 1
        net_zones[net_zone_name].chances_for += 1

def calculate_map_stats(shooter_tags: list[PlayerStatsTag]) -> tuple[dict[str, ZoneData], dict[str, ZoneData], list[MarkerData], list[MarkerData]]:
    ice_zones = defaultdict(ZoneData)
    net_zones = defaultdict(ZoneData)
    ice_markers: list[MarkerData] = []
    net_markers: list[MarkerData] = []

    for tag in shooter_tags:
        if should_skip_tag(tag):
            continue

        add_markers(tag, ice_markers, net_markers)
        increment_zone_data(tag, ice_zones, net_zones)

    return ice_zones, net_zones, ice_markers, net_markers
