from pydantic import BaseModel


class ZoneData(BaseModel):
    """Per-zone statistics for all metrics"""

    goals_for: int = 0
    goals_against: int = 0
    chances_for: int = 0
    chances_against: int = 0
