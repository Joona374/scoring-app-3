from db.models import PlayerStatsTag, ShotResultTypes
from db.pydantic_schema.player_page import ShotTypeStats

def calculate_shot_type_stats(shooter_tags: list[PlayerStatsTag]) -> list[ShotTypeStats]:
    stats_dict: dict[str, ShotTypeStats] = {}
    for tag in shooter_tags:
        shot_type = tag.shot_type.value.value if tag.shot_type else "UNKNOWN"
        result = tag.shot_result.value

        if shot_type not in stats_dict:
            stats_dict[shot_type] = ShotTypeStats(shot_type=shot_type)
            
        stat = stats_dict[shot_type]

        if result == ShotResultTypes.GOAL_FOR:
            stat.goals += 1
            stat.chances += 1

        elif result == ShotResultTypes.CHANCE_FOR:
            stat.chances += 1

    for stat in stats_dict.values():
        if stat.chances > 0:
            stat.efficiency = round((stat.goals / stat.chances * 100), 1)

    return list(stats_dict.values())
