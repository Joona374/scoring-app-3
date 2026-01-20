import { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";
import LoadingSpinner from "../../components/LoadingSpinner/LoadingSpinner";
import IceZoneMap from "./components/IceZoneMap";
import NetZoneMap from "./components/NetZoneMap";
import { getCachedDashboard, cacheDashboard } from "../../utils/dashboardCache";
import ScrollContainer from "../../components/ScrollContainer/ScrollContainer";

export default function TeamDashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [gamesCount, setGamesCount] = useState(null); // null = all games
  const [zoneMode, setZoneMode] = useState("goals_for"); // Current zone display mode
  const [sortConfig, setSortConfig] = useState({
    key: "chances_plus_minus_on_ice",
    direction: "desc",
  });
  const navigate = useNavigate();

  useEffect(() => {
    // Try to load from cache first for instant display
    const cached = getCachedDashboard();
    if (cached) {
      setDashboardData(cached);
      setGamesCount(cached.games.length);
      setLoading(false); // Show cached data immediately
    }

    // Always fetch fresh data (updates silently when ready)
    const fetchDashboard = async () => {
      const token = sessionStorage.getItem("jwt_token");
      const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

      try {
        const response = await fetch(`${BACKEND_URL}/dashboard`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.status === 404) {
          navigate("/create-team");
          return;
        }

        if (!response.ok) {
          throw new Error("Virhe tietojen haussa");
        }

        const data = await response.json();

        // Cache for next time
        cacheDashboard(data);

        setDashboardData(data);
        setGamesCount(data.games.length);
      } catch (err) {
        console.error("Dashboard error:", err);
        // Only show error if we don't have cached data
        if (!cached) {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, [navigate]);

  // Filter games based on slider
  const filteredGames = useMemo(() => {
    if (!dashboardData?.games) return [];
    return dashboardData.games.slice(
      0,
      gamesCount || dashboardData.games.length,
    );
  }, [dashboardData?.games, gamesCount]);

  // Calculate totals from filtered games
  const totals = useMemo(() => {
    if (filteredGames.length === 0) {
      return {
        goals_for: 0,
        goals_against: 0,
        chances_for: 0,
        chances_against: 0,
        efficiency_for: 0,
        efficiency_against: 0,
      };
    }

    const gf = filteredGames.reduce((sum, g) => sum + g.goals_for, 0);
    const ga = filteredGames.reduce((sum, g) => sum + g.goals_against, 0);
    const cf = filteredGames.reduce((sum, g) => sum + g.chances_for, 0);
    const ca = filteredGames.reduce((sum, g) => sum + g.chances_against, 0);

    return {
      goals_for: gf,
      goals_against: ga,
      chances_for: cf,
      chances_against: ca,
      efficiency_for: cf > 0 ? Math.round((gf / cf) * 1000) / 10 : 0,
      efficiency_against: ca > 0 ? Math.round((ga / ca) * 1000) / 10 : 0,
    };
  }, [filteredGames]);

  // Calculate mean and standard deviation for games table coloring
  const gameStats = useMemo(() => {
    if (filteredGames.length === 0) {
      return {
        goalsFor: { mean: 0, sd: 1 },
        goalsAgainst: { mean: 0, sd: 1 },
        chancesFor: { mean: 0, sd: 1 },
        chancesAgainst: { mean: 0, sd: 1 },
      };
    }

    const calcMeanAndSD = (values) => {
      const n = values.length;
      const mean = values.reduce((a, b) => a + b, 0) / n;
      const variance =
        values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / n;
      const sd = Math.sqrt(variance) || 1; // Avoid division by zero
      return { mean, sd };
    };

    return {
      goalsFor: calcMeanAndSD(filteredGames.map((g) => g.goals_for)),
      goalsAgainst: calcMeanAndSD(filteredGames.map((g) => g.goals_against)),
      chancesFor: calcMeanAndSD(filteredGames.map((g) => g.chances_for)),
      chancesAgainst: calcMeanAndSD(
        filteredGames.map((g) => g.chances_against),
      ),
    };
  }, [filteredGames]);

  // Aggregate zone stats from filtered games
  const aggregatedZoneStats = useMemo(() => {
    const ice_zones = {};
    const net_zones = {};

    for (const game of filteredGames) {
      // Aggregate ice zones
      for (const [zoneName, zoneData] of Object.entries(game.ice_zones || {})) {
        if (!ice_zones[zoneName]) {
          ice_zones[zoneName] = {
            goals_for: 0,
            goals_against: 0,
            chances_for: 0,
            chances_against: 0,
          };
        }
        ice_zones[zoneName].goals_for += zoneData.goals_for;
        ice_zones[zoneName].goals_against += zoneData.goals_against;
        ice_zones[zoneName].chances_for += zoneData.chances_for;
        ice_zones[zoneName].chances_against += zoneData.chances_against;
      }

      // Aggregate net zones
      for (const [zoneName, zoneData] of Object.entries(game.net_zones || {})) {
        if (!net_zones[zoneName]) {
          net_zones[zoneName] = {
            goals_for: 0,
            goals_against: 0,
            chances_for: 0,
            chances_against: 0,
          };
        }
        net_zones[zoneName].goals_for += zoneData.goals_for;
        net_zones[zoneName].goals_against += zoneData.goals_against;
        net_zones[zoneName].chances_for += zoneData.chances_for;
        net_zones[zoneName].chances_against += zoneData.chances_against;
      }
    }

    return { ice_zones, net_zones };
  }, [filteredGames]);

  // Aggregate player stats from filtered games
  const aggregatedPlayers = useMemo(() => {
    const playerMap = {};

    for (const game of filteredGames) {
      for (const ps of game.player_stats || []) {
        if (!playerMap[ps.player_id]) {
          playerMap[ps.player_id] = {
            player_id: ps.player_id,
            first_name: ps.first_name,
            last_name: ps.last_name,
            jersey_number: ps.jersey_number,
            games_played: 0,
            goals: 0,
            chances: 0,
            goals_plus_on_ice: 0,
            goals_minus_on_ice: 0,
            chances_plus_on_ice: 0,
            chances_minus_on_ice: 0,
            goals_plus_participating: 0,
            goals_minus_participating: 0,
            chances_plus_participating: 0,
            chances_minus_participating: 0,
          };
        }

        const p = playerMap[ps.player_id];
        p.games_played += 1;
        p.goals += ps.goals;
        p.chances += ps.chances;
        p.goals_plus_on_ice += ps.goals_plus_on_ice;
        p.goals_minus_on_ice += ps.goals_minus_on_ice;
        p.chances_plus_on_ice += ps.chances_plus_on_ice;
        p.chances_minus_on_ice += ps.chances_minus_on_ice;
        p.goals_plus_participating += ps.goals_plus_participating;
        p.goals_minus_participating += ps.goals_minus_participating;
        p.chances_plus_participating += ps.chances_plus_participating;
        p.chances_minus_participating += ps.chances_minus_participating;
      }
    }

    // Calculate derived fields
    return Object.values(playerMap).map((p) => ({
      ...p,
      efficiency:
        p.chances > 0 ? Math.round((p.goals / p.chances) * 1000) / 10 : 0,
      goals_plus_minus_on_ice: p.goals_plus_on_ice - p.goals_minus_on_ice,
      goals_plus_minus_participating:
        p.goals_plus_participating - p.goals_minus_participating,
      chances_plus_minus_on_ice:
        p.chances_plus_on_ice +
        p.goals_plus_on_ice -
        (p.chances_minus_on_ice + p.goals_minus_on_ice),
      chances_plus_minus_participating:
        p.chances_plus_participating +
        p.goals_plus_participating -
        (p.chances_minus_participating + p.goals_minus_participating),
    }));
  }, [filteredGames]);

  // Sort players
  const sortedPlayers = useMemo(() => {
    if (aggregatedPlayers.length === 0) return [];

    const sorted = [...aggregatedPlayers].sort((a, b) => {
      const aVal = a[sortConfig.key];
      const bVal = b[sortConfig.key];

      if (sortConfig.direction === "asc") {
        return aVal - bVal;
      }
      return bVal - aVal;
    });

    return sorted;
  }, [aggregatedPlayers, sortConfig]);

  const handleSort = (key) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === "desc" ? "asc" : "desc",
    }));
  };

  const getSortIndicator = (key) => {
    if (sortConfig.key !== key) return "";
    return sortConfig.direction === "desc" ? " ▼" : " ▲";
  };

  if (loading) {
    return (
      <ScrollContainer className="dashboard-wrapper">
        <header className="dashboard-header">
          <h1 className="dashboard-title">Ladataan...</h1>
          <p className="dashboard-subtitle">Haetaan joukkueen tietoja</p>
        </header>
        <div className="loading-container">
          <LoadingSpinner size={40} />
          <p className="loading-hint">
            Tämä voi kestää hetken, jos palvelin oli lepotilassa.
          </p>
        </div>
      </ScrollContainer>
    );
  }

  if (error) {
    return (
      <ScrollContainer className="dashboard-wrapper">
        <header className="dashboard-header">
          <h1 className="dashboard-title">Virhe</h1>
        </header>
        <p className="dashboard-error">{error}</p>
      </ScrollContainer>
    );
  }

  if (!dashboardData) {
    return null;
  }

  const { team_name, games } = dashboardData;
  const totalGamesCount = games.length;

  return (
    <ScrollContainer className="dashboard-wrapper">
      <header className="dashboard-header">
        <h1 className="dashboard-title">{team_name}</h1>
        <p className="dashboard-subtitle">
          {gamesCount === totalGamesCount
            ? `Kausi ${totalGamesCount} peliä`
            : `Viimeiset ${gamesCount} / ${totalGamesCount} peliä`}
        </p>
      </header>

      {/* Games Slider */}
      <section className="games-slider-section">
        <label className="slider-label">
          Näytä tilastot:
          <input
            type="range"
            min="1"
            max={totalGamesCount}
            value={gamesCount || totalGamesCount}
            onChange={(e) => setGamesCount(Number(e.target.value))}
            className="games-slider"
          />
          <span className="slider-value">{gamesCount} peliä</span>
        </label>
      </section>

      {/* KPIs for selected games */}
      <section className="season-kpis">
        <div className="kpi-grid">
          <div className="kpi-card">
            <span className="kpi-value">{totals.goals_for}</span>
            <span className="kpi-label">Maalit +</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-value">{totals.goals_against}</span>
            <span className="kpi-label">Maalit -</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-value">{totals.chances_for}</span>
            <span className="kpi-label">Maalipaikat +</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-value">{totals.chances_against}</span>
            <span className="kpi-label">Maalipaikat -</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-value">{totals.efficiency_for}%</span>
            <span className="kpi-label">Tehokkuus</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-value">{totals.efficiency_against}%</span>
            <span className="kpi-label">Tehokkuus vast.</span>
          </div>
        </div>
      </section>

      {/* Zone Maps */}
      <section className="zone-maps-section">
        <div className="zone-maps-grid">
          <div className="zone-map-wrapper">
            <h3 className="zone-map-title">Laukaisupaikat</h3>
            <IceZoneMap
              zoneStats={aggregatedZoneStats.ice_zones}
              mode={zoneMode}
              totals={totals}
            />
          </div>

          {/* Zone Mode Selector - between the two maps */}
          <div className="zone-mode-grid">
            <div className="mode-column">
              <span className="mode-column-title">Lukumäärä</span>
              <button
                className={`mode-btn ${zoneMode === "goals_for" ? "active" : ""}`}
                onClick={() => setZoneMode("goals_for")}
              >
                Maali+
              </button>
              <button
                className={`mode-btn ${zoneMode === "goals_against" ? "active" : ""}`}
                onClick={() => setZoneMode("goals_against")}
              >
                Maali-
              </button>
              <button
                className={`mode-btn ${zoneMode === "chances_for" ? "active" : ""}`}
                onClick={() => setZoneMode("chances_for")}
              >
                MP+
              </button>
              <button
                className={`mode-btn ${zoneMode === "chances_against" ? "active" : ""}`}
                onClick={() => setZoneMode("chances_against")}
              >
                MP-
              </button>
            </div>
            <div className="mode-column">
              <span className="mode-column-title">% kaikista</span>
              <button
                className={`mode-btn ${zoneMode === "goals_for_pct" ? "active" : ""}`}
                onClick={() => setZoneMode("goals_for_pct")}
              >
                Maali+ %
              </button>
              <button
                className={`mode-btn ${zoneMode === "goals_against_pct" ? "active" : ""}`}
                onClick={() => setZoneMode("goals_against_pct")}
              >
                Maali- %
              </button>
              <button
                className={`mode-btn ${zoneMode === "chances_for_pct" ? "active" : ""}`}
                onClick={() => setZoneMode("chances_for_pct")}
              >
                MP+ %
              </button>
              <button
                className={`mode-btn ${zoneMode === "chances_against_pct" ? "active" : ""}`}
                onClick={() => setZoneMode("chances_against_pct")}
              >
                MP- %
              </button>
            </div>
            <div className="mode-column">
              <span className="mode-column-title">+/- & Teho</span>
              <button
                className={`mode-btn ${zoneMode === "goals_diff" ? "active" : ""}`}
                onClick={() => setZoneMode("goals_diff")}
              >
                Maali +/-
              </button>
              <button
                className={`mode-btn ${zoneMode === "chances_diff" ? "active" : ""}`}
                onClick={() => setZoneMode("chances_diff")}
              >
                MP +/-
              </button>
              <button
                className={`mode-btn ${zoneMode === "efficiency_for" ? "active" : ""}`}
                onClick={() => setZoneMode("efficiency_for")}
              >
                MP+ teho%
              </button>
              <button
                className={`mode-btn ${zoneMode === "efficiency_against" ? "active" : ""}`}
                onClick={() => setZoneMode("efficiency_against")}
              >
                MP- teho%
              </button>
            </div>
          </div>

          <div className="zone-map-wrapper">
            <h3 className="zone-map-title">Maalipaikat</h3>
            <NetZoneMap
              zoneStats={aggregatedZoneStats.net_zones}
              mode={zoneMode}
              totals={totals}
            />
          </div>
        </div>
      </section>

      <div className="dashboard-grid">
        {/* Player Stats Table */}
        <section className="dashboard-section">
          <h2 className="section-title">
            Pelaajatilastot ({sortedPlayers.length} pelaajaa)
            <span className="section-hint">
              {" "}
              (klikkaa saraketta järjestääksesi)
            </span>
          </h2>
          <div className="table-container">
            <table className="dashboard-table players-table">
              <thead>
                <tr>
                  <th>Pelaaja</th>
                  <SortableHeader
                    label="Pelit"
                    sortKey="games_played"
                    currentSort={sortConfig}
                    onSort={handleSort}
                    getSortIndicator={getSortIndicator}
                  />
                  <SortableHeader
                    label="Maalit"
                    sortKey="goals"
                    currentSort={sortConfig}
                    onSort={handleSort}
                    getSortIndicator={getSortIndicator}
                  />
                  <SortableHeader
                    label="MP"
                    sortKey="chances"
                    currentSort={sortConfig}
                    onSort={handleSort}
                    getSortIndicator={getSortIndicator}
                  />
                  <SortableHeader
                    label="MP%"
                    sortKey="efficiency"
                    currentSort={sortConfig}
                    onSort={handleSort}
                    getSortIndicator={getSortIndicator}
                  />
                  <SortableHeader
                    label="Maalit+/- (osall.)"
                    sortKey="goals_plus_minus_participating"
                    currentSort={sortConfig}
                    onSort={handleSort}
                    getSortIndicator={getSortIndicator}
                  />
                  <SortableHeader
                    label="Maalit+/- (jää)"
                    sortKey="goals_plus_minus_on_ice"
                    currentSort={sortConfig}
                    onSort={handleSort}
                    getSortIndicator={getSortIndicator}
                  />
                  <SortableHeader
                    label="MP+/- (osall.)"
                    sortKey="chances_plus_minus_participating"
                    currentSort={sortConfig}
                    onSort={handleSort}
                    getSortIndicator={getSortIndicator}
                  />
                  <SortableHeader
                    label="MP+/- (jää)"
                    sortKey="chances_plus_minus_on_ice"
                    currentSort={sortConfig}
                    onSort={handleSort}
                    getSortIndicator={getSortIndicator}
                  />
                </tr>
              </thead>
              <tbody>
                {sortedPlayers.length > 0 ? (
                  sortedPlayers.map((player) => (
                    <tr key={player.player_id}>
                      <td className="dashboard-player-info">
                        <span className="dashboard-player-number">
                          #{player.jersey_number}
                        </span>
                        <span className="dashboard-player-name">
                          {player.first_name[0]}. {player.last_name}
                        </span>
                      </td>
                      <td>{player.games_played}</td>
                      <td>{player.goals}</td>
                      <td>{player.chances}</td>
                      <td>{player.efficiency}%</td>
                      <td
                        className={getPlusMinusClass(
                          player.goals_plus_minus_participating,
                        )}
                      >
                        {formatPlusMinus(player.goals_plus_minus_participating)}
                      </td>
                      <td
                        className={getPlusMinusClass(
                          player.goals_plus_minus_on_ice,
                        )}
                      >
                        {formatPlusMinus(player.goals_plus_minus_on_ice)}
                      </td>
                      <td
                        className={getPlusMinusClass(
                          player.chances_plus_minus_participating,
                        )}
                      >
                        {formatPlusMinus(
                          player.chances_plus_minus_participating,
                        )}
                      </td>
                      <td
                        className={getPlusMinusClass(
                          player.chances_plus_minus_on_ice,
                        )}
                      >
                        {formatPlusMinus(player.chances_plus_minus_on_ice)}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={9} className="no-data">
                      Ei pelaajatietoja
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        {/* Games KPI Table */}
        <section className="dashboard-section">
          <h2 className="section-title">
            {gamesCount === totalGamesCount
              ? "Kaikki pelit"
              : `Viimeiset ${gamesCount} peliä`}
          </h2>
          <div className="table-container">
            <table className="dashboard-table dashboard-games-table">
              <thead>
                <tr>
                  <th>Peli</th>
                  <th>M+</th>
                  <th>M-</th>
                  <th>MP+</th>
                  <th>MP-</th>
                  <th>MP+ %</th>
                  <th>MP- %</th>
                </tr>
              </thead>
              <tbody>
                {filteredGames.map((game, index) => {
                  // Determine win/loss/draw
                  const result =
                    game.goals_for > game.goals_against
                      ? "win"
                      : game.goals_for < game.goals_against
                        ? "loss"
                        : "draw";
                  const resultClass =
                    result === "win"
                      ? "game-win"
                      : result === "loss"
                        ? "game-loss"
                        : "";

                  // Check if stat is 1+ SD from mean (for coloring)
                  const isOutlier = (value, stats, isPositive) => {
                    const deviation = (value - stats.mean) / stats.sd;
                    // For positive stats (M+, MP+): highlight if above average
                    // For negative stats (M-, MP-): highlight if below average (fewer against is good)
                    if (isPositive) {
                      return deviation >= 1
                        ? "stat-positive"
                        : deviation <= -1
                          ? "stat-negative"
                          : "";
                    } else {
                      return deviation <= -1
                        ? "stat-positive"
                        : deviation >= 1
                          ? "stat-negative"
                          : "";
                    }
                  };

                  return (
                    <tr key={game.game_id || index}>
                      <td className="game-info">
                        <span className={`game-opponent ${resultClass}`}>
                          {game.opponent} ({game.home ? "K" : "V"})
                        </span>
                        <span className={`game-date ${resultClass}`}>
                          {formatDate(game.date)}
                        </span>
                      </td>
                      <td
                        className={isOutlier(
                          game.goals_for,
                          gameStats.goalsFor,
                          true,
                        )}
                      >
                        {game.goals_for}
                      </td>
                      <td
                        className={isOutlier(
                          game.goals_against,
                          gameStats.goalsAgainst,
                          false,
                        )}
                      >
                        {game.goals_against}
                      </td>
                      <td
                        className={isOutlier(
                          game.chances_for,
                          gameStats.chancesFor,
                          true,
                        )}
                      >
                        {game.chances_for}
                      </td>
                      <td
                        className={isOutlier(
                          game.chances_against,
                          gameStats.chancesAgainst,
                          false,
                        )}
                      >
                        {game.chances_against}
                      </td>
                      <td>{game.efficiency_for}%</td>
                      <td>{game.efficiency_against}%</td>
                    </tr>
                  );
                })}
                {/* Totals row */}
                <tr className="totals-row">
                  <td className="totals-label">Yhteensä</td>
                  <td>{totals.goals_for}</td>
                  <td>{totals.goals_against}</td>
                  <td>{totals.chances_for}</td>
                  <td>{totals.chances_against}</td>
                  <td>{totals.efficiency_for}%</td>
                  <td>{totals.efficiency_against}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </ScrollContainer>
  );
}

// =====================
// Helper Components
// =====================

function SortableHeader({
  label,
  sortKey,
  currentSort,
  onSort,
  getSortIndicator,
}) {
  const isActive = currentSort.key === sortKey;

  return (
    <th
      className={`sortable-header ${isActive ? "active" : ""}`}
      onClick={() => onSort(sortKey)}
    >
      {label}
      {getSortIndicator(sortKey)}
    </th>
  );
}

// =====================
// Helper Functions
// =====================

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString("fi-FI", {
    day: "numeric",
    month: "numeric",
  });
}

function formatPlusMinus(value) {
  if (value > 0) return `+${value}`;
  return value.toString();
}

function getPlusMinusClass(value) {
  if (value > 0) return "stat-positive";
  if (value < 0) return "stat-negative";
  return "";
}
