from db.models import PlayerStatsTag, ShotResultTypes
from db.pydantic_schema.player_page import SeasonSummaryKPIs

def aggregate_shooter_kpis(shooter_tags: list[PlayerStatsTag], summary: SeasonSummaryKPIs) -> None:
    """
    Extracts shooter-specific KPIs from the provided tags and updates the summary object in place accordingly.
    """
    for tag in shooter_tags:
        result = tag.shot_result.value
        if result == ShotResultTypes.GOAL_FOR:
            summary.goals += 1
            summary.chances += 1
        elif result == ShotResultTypes.CHANCE_FOR:
            summary.chances += 1

    summary.efficiency = round((summary.goals / summary.chances * 100), 1) if summary.chances > 0 else 0.0
    summary.chances_per_game = round((summary.chances / summary.games_played), 1) if summary.games_played > 0 else 0.0

def aggregate_participation_kpis(participating_tags: list[PlayerStatsTag], summary: SeasonSummaryKPIs) -> None:
    for tag in participating_tags:
        result = tag.shot_result.value
        if result == ShotResultTypes.GOAL_FOR:
            summary.participation_m_plus += 1
            summary.participation_mp_plus += 1
        elif result == ShotResultTypes.GOAL_AGAINST:
            summary.participation_m_minus += 1
            summary.participation_mp_minus += 1
        elif result == ShotResultTypes.CHANCE_FOR:
            summary.participation_mp_plus += 1
        elif result == ShotResultTypes.CHANCE_AGAINST:
            summary.participation_mp_minus += 1

    # +/- Per Game
    denom = max(summary.games_played, 1)
    summary.participation_m_diff = round((summary.participation_m_plus - summary.participation_m_minus) / denom, 2)
    summary.participation_mp_diff = round((summary.participation_mp_plus - summary.participation_mp_minus) / denom, 2)


def aggregate_on_ice_kpis(on_ice_tags: list[PlayerStatsTag], summary: SeasonSummaryKPIs) -> None:
    for tag in on_ice_tags:
        result = tag.shot_result.value
        if result == ShotResultTypes.GOAL_FOR:
            summary.on_ice_m_plus += 1
            summary.on_ice_mp_plus += 1
        elif result == ShotResultTypes.GOAL_AGAINST:
            summary.on_ice_m_minus += 1
            summary.on_ice_mp_minus += 1
        elif result == ShotResultTypes.CHANCE_FOR:
            summary.on_ice_mp_plus += 1
        elif result == ShotResultTypes.CHANCE_AGAINST:
            summary.on_ice_mp_minus += 1

    # +/- Per Game
    denom = max(summary.games_played, 1)
    summary.on_ice_m_diff = round((summary.on_ice_m_plus - summary.on_ice_m_minus) / denom, 2)
    summary.on_ice_mp_diff = round((summary.on_ice_mp_plus - summary.on_ice_mp_minus) / denom, 2)

def calculate_summary_kpis(games_played: int, shooter_tags: list[PlayerStatsTag], on_ice_tags: list[PlayerStatsTag], participating_tags: list[PlayerStatsTag]) -> SeasonSummaryKPIs:
    summary = SeasonSummaryKPIs(games_played=games_played)
    aggregate_shooter_kpis(shooter_tags, summary)
    aggregate_participation_kpis(participating_tags, summary)
    aggregate_on_ice_kpis(on_ice_tags, summary)
    return summary
