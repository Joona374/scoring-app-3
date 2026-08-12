from pydantic import BaseModel


class MarkerData(BaseModel):
    x: int
    y: int
    result: str


class PlayerTagData(BaseModel):
    id: int
    game_id: int
    date: str
    opponent: str
    home: bool
    strengths: str
    ice_x: int
    ice_y: int
    ice_zone: str
    net_x: int
    net_y: int
    net_zone: str
    net_height: str
    net_width: str
    shot_result: str
    shot_type: str
    is_shooter: bool
    is_participating: bool
    is_on_ice: bool


class PlayerGameMetadata(BaseModel):
    game_id: int
    date: str
    opponent: str
    home: bool


class ShotTypeStats(BaseModel):
    shot_type: str
    goals: int = 0
    chances: int = 0
    efficiency: float = 0.0


class GameTrendPoint(BaseModel):
    game_id: int
    opponent: str
    date: str
    goals: int
    chances: int
    rolling_goals: float
    rolling_chances: float
    team_rolling_goals: float
    team_rolling_chances: float


class SpiderChartKPI(BaseModel):
    label: str
    player_value: float
    team_avg: float


class SpiderChartData(BaseModel):
    kpis: list[SpiderChartKPI]


class SynergyDataPoint(BaseModel):
    teammate_id: int
    teammate_name: str
    jersey_number: int
    net_mp_per_game: float
    shared_games: int


class SynergyData(BaseModel):
    points: list[SynergyDataPoint]


class ChemistryTeammate(BaseModel):
    teammate_id: int
    name: str
    jersey_number: int
    position: str
    shared_games: int
    shared_participations: int
    shared_goals: int
    participations_per_game: float
    efficiency: float


class ChemistrySectionData(BaseModel):
    teammates: list[ChemistryTeammate]
    team_avg_volume: float
    team_avg_efficiency: float


class GameLogEntry(BaseModel):
    game_id: int
    date: str
    opponent: str
    home: bool
    goals: int
    chances: int
    efficiency: float
    part_m_plus: int
    part_m_minus: int
    part_m_diff: int
    part_mp_plus: int
    part_mp_minus: int
    part_mp_diff: int
    onice_m_plus: int
    onice_m_minus: int
    onice_m_diff: int
    onice_mp_plus: int
    onice_mp_minus: int
    onice_mp_diff: int


class PlayerStatsResponse(BaseModel):
    player_id: int
    first_name: str
    last_name: str
    jersey_number: int
    position: str
    team_name: str
    all_tags: list[PlayerTagData]
    all_games: list[PlayerGameMetadata]
    trend_data: list[GameTrendPoint]
    spider_data: SpiderChartData
    synergy_data: SynergyData
    chemistry_data: ChemistrySectionData
    game_log: list[GameLogEntry]
    # Future components will add more fields here


class SeasonSummaryKPIs(BaseModel):
    games_played: int = 0
    goals: int = 0
    chances: int = 0
    efficiency: float = 0.0
    chances_per_game: float = 0.0
    participation_m_plus: int = 0
    participation_m_minus: int = 0
    participation_m_diff: float = 0  # Per game
    participation_mp_plus: int = 0
    participation_mp_minus: int = 0
    participation_mp_diff: float = 0  # Per game
    on_ice_m_plus: int = 0
    on_ice_m_minus: int = 0
    on_ice_m_diff: float = 0  # Per game
    on_ice_mp_plus: int = 0
    on_ice_mp_minus: int = 0
    on_ice_mp_diff: float = 0  # Per game
