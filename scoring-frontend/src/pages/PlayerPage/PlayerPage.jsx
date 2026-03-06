import { useEffect, useState, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "./PlayerPage.css";
import LoadingSpinner from "../../components/LoadingSpinner/LoadingSpinner";
import ScrollContainer from "../../components/ScrollContainer/ScrollContainer";
import PlayerHeader from "./components/PlayerHeader";
import PlayerKPIs from "./components/PlayerKPIs";
import PlayerIceMap from "./components/PlayerIceMap";
import PlayerNetMap from "./components/PlayerNetMap";
import PlayerFilters from "./components/PlayerFilters";
import ShotTypeTable from "./components/ShotTypeTable";
import RollingAverageChart from "./components/RollingAverageChart";
import PlayerSpiderChart from "./components/PlayerSpiderChart";
import OnIceSynergyChart from "./components/OnIceSynergyChart";
import ChemistrySection from "./components/ChemistrySection";

export default function PlayerPage() {
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [playerData, setPlayerData] = useState(null);
  
  const [mapMode, setMapMode] = useState("kaikki"); 
  const [vizType, setVizType] = useState("markers"); 
  
  const [filters, setFilters] = useState({
    situation: "ALL",
    venue: "ALL",
    startDate: null,
    endDate: null,
    lastGames: null,
  });

  const navigate = useNavigate();

  useEffect(() => {
    const fetchPlayerStats = async () => {
      const token = sessionStorage.getItem("jwt_token");
      const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

      try {
        const response = await fetch(`${BACKEND_URL}/players/${id}/stats`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          if (response.status === 404) throw new Error("Pelaajaa ei löytynyt");
          if (response.status === 403) throw new Error("Ei oikeutta pelaajan tietoihin");
          throw new Error("Virhe tietojen haussa");
        }

        const data = await response.json();
        setPlayerData(data);
        setFilters(prev => ({ ...prev, lastGames: data.all_games.length }));
      } catch (err) {
        console.error("PlayerPage error:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPlayerStats();
  }, [id]);

  const filteredData = useMemo(() => {
    if (!playerData) return null;

    // 1. Filter games
    let games = [...playerData.all_games];
    if (filters.venue !== "ALL") {
      const isHome = filters.venue === "HOME";
      games = games.filter(g => g.home === isHome);
    }
    if (filters.startDate) {
      games = games.filter(g => g.date >= filters.startDate);
    }
    if (filters.endDate) {
      games = games.filter(g => g.date <= filters.endDate);
    }

    const gamesInSelection = games.slice(0, filters.lastGames || games.length);
    const activeGameIds = new Set(gamesInSelection.map(g => g.game_id));

    // 2. Filter tags
    let tags = playerData.all_tags.filter(t => activeGameIds.has(t.game_id));
    if (filters.situation !== "ALL") {
      tags = tags.filter(t => t.strengths === filters.situation);
    }

    // 3. Calculate Summary KPIs
    const summary = {
      games_played: gamesInSelection.length,
      goals: 0,
      chances: 0,
      efficiency: 0,
      chances_per_game: 0,
      participation_m_diff: 0,
      participation_mp_diff: 0,
      on_ice_m_diff: 0,
      on_ice_mp_diff: 0,
    };

    let p_m_plus = 0, p_m_minus = 0, p_mp_plus = 0, p_mp_minus = 0;
    let o_m_plus = 0, o_m_minus = 0, o_mp_plus = 0, o_mp_minus = 0;

    const shotTypesMap = {};

    tags.forEach(t => {
      const isGoalFor = t.shot_result === "Maali +";
      const isGoalAgainst = t.shot_result === "Maali -";
      const isChanceFor = t.shot_result === "MP +";
      const isChanceAgainst = t.shot_result === "MP -";

      if (t.is_shooter) {
        if (isGoalFor) { summary.goals++; summary.chances++; }
        else if (isChanceFor) { summary.chances++; }

        if (isGoalFor || isChanceFor) {
          if (!shotTypesMap[t.shot_type]) {
            shotTypesMap[t.shot_type] = { shot_type: t.shot_type, goals: 0, chances: 0, efficiency: 0 };
          }
          if (isGoalFor) {
            shotTypesMap[t.shot_type].goals++;
            shotTypesMap[t.shot_type].chances++;
          } else {
            shotTypesMap[t.shot_type].chances++;
          }
        }
      }

      if (t.is_participating) {
        if (isGoalFor) { p_m_plus++; p_mp_plus++; }
        else if (isGoalAgainst) { p_m_minus++; p_mp_minus++; }
        else if (isChanceFor) { p_mp_plus++; }
        else if (isChanceAgainst) { p_mp_minus++; }
      }

      if (t.is_on_ice) {
        if (isGoalFor) { o_m_plus++; o_mp_plus++; }
        else if (isGoalAgainst) { o_m_minus++; o_mp_minus++; }
        else if (isChanceFor) { o_mp_plus++; }
        else if (isChanceAgainst) { o_mp_minus++; }
      }
    });

    summary.efficiency = summary.chances > 0 ? Math.round((summary.goals / summary.chances) * 1000) / 10 : 0;
    summary.chances_per_game = summary.games_played > 0 ? Math.round((summary.chances / summary.games_played) * 10) / 10 : 0;
    summary.participation_m_diff = p_m_plus - p_m_minus;
    summary.participation_mp_diff = p_mp_plus - p_mp_minus;
    summary.on_ice_m_diff = o_m_plus - o_m_minus;
    summary.on_ice_mp_diff = o_mp_plus - o_mp_minus;

    const shot_type_stats = Object.values(shotTypesMap).map(s => ({
      ...s,
      efficiency: s.chances > 0 ? Math.round((s.goals / s.chances) * 1000) / 10 : 0
    }));

    // 4. Calculate Map Data
    const ice_zones = {};
    const net_zones = {};
    const ice_markers = [];
    const net_markers = [];

    const mapTags = tags.filter(t => t.is_shooter);
    mapTags.forEach(tag => {
      const res = tag.shot_result;
      const isGoal = res === "Maali +";
      const isChance = res === "MP +";
      if (!isGoal && !isChance) return;

      const showInMarkers = mapMode === "kaikki" || (mapMode === "goals" && isGoal) || (mapMode === "chances" && !isGoal);
      if (showInMarkers) {
        ice_markers.push({ x: tag.ice_x, y: tag.ice_y, result: res });
        net_markers.push({ x: tag.net_x, y: tag.net_y, result: res });
      }

      const addToZone = (zones, name, isGoal) => {
        if (!zones[name]) zones[name] = { goals_for: 0, chances_for: 0 };
        if (isGoal) {
          zones[name].goals_for++;
          zones[name].chances_for++;
        } else {
          zones[name].chances_for++;
        }
      };
      addToZone(ice_zones, tag.ice_zone, isGoal);
      addToZone(net_zones, tag.net_zone, isGoal);
    });

    const trend_data = playerData.trend_data.filter(tp => activeGameIds.has(tp.game_id))
                        .sort((a, b) => a.date.localeCompare(b.date));

    return { 
      summary, 
      ice_zones,
      net_zones,
      ice_markers, 
      net_markers,
      shot_type_stats,
      trend_data, 
      availableGamesCount: games.length
    };
  }, [playerData, filters, mapMode]);

  if (loading) {
    return (
      <ScrollContainer className="player-page-wrapper">
        <div className="loading-container">
          <LoadingSpinner size={40} />
          <p>Ladataan pelaajan tietoja...</p>
        </div>
      </ScrollContainer>
    );
  }

  if (error) {
    return (
      <ScrollContainer className="player-page-wrapper">
        <header className="player-page-header">
          <h1 className="player-page-title">Virhe</h1>
        </header>
        <p className="player-page-error">{error}</p>
        <button onClick={() => navigate("/dashboard")} className="back-btn">
          Takaisin dashboardille
        </button>
      </ScrollContainer>
    );
  }

  const finalVizType = mapMode === "efficiency" ? "zones" : vizType;

  return (
    <ScrollContainer className="player-page-wrapper">
      <PlayerHeader player={playerData} />
      
      <PlayerFilters 
        filters={filters} 
        setFilters={setFilters} 
        availableGamesCount={filteredData.availableGamesCount}
      />

      <PlayerKPIs summary={filteredData.summary} />

      <section className="player-visualizations-section">
        <div className="player-visualizations-grid">
          <div className="player-map-wrapper ice-map-large">
            <h3 className="player-map-title">Laukaisupaikat</h3>
            <PlayerIceMap 
              zoneStats={filteredData.ice_zones} 
              markers={filteredData.ice_markers}
              mode={mapMode === "kaikki" ? "chances_for" : (mapMode === "goals" ? "goals_for" : (mapMode === "chances" ? "chances_for_no_goals" : "efficiency_for"))}
              showMarkers={finalVizType === "markers"}
              showZones={finalVizType === "zones"}
            />
          </div>

          <div className="player-map-controls-wrapper">
             <div className="player-map-controls">
                <div className="control-group">
                  <span className="control-label">Näkymä</span>
                  <div className="viz-type-toggle">
                    <button 
                      className={`toggle-btn ${finalVizType === "markers" ? "active" : ""}`}
                      onClick={() => setVizType("markers")}
                      disabled={mapMode === "efficiency"}
                    >
                      Paikoittain
                    </button>
                    <button 
                      className={`toggle-btn ${finalVizType === "zones" ? "active" : ""}`}
                      onClick={() => setVizType("zones")}
                    >
                      Alueittain
                    </button>
                  </div>
                </div>

                <div className="control-group">
                  <span className="control-label">Tilasto</span>
                  <div className="mode-options-grid">
                    <button 
                      className={`control-btn ${mapMode === "kaikki" ? "active" : ""}`}
                      onClick={() => setMapMode("kaikki")}
                    >
                      Kaikki
                    </button>
                    <button 
                      className={`control-btn ${mapMode === "goals" ? "active" : ""}`}
                      onClick={() => setMapMode("goals")}
                    >
                      Maalit
                    </button>
                    <button 
                      className={`control-btn ${mapMode === "chances" ? "active" : ""}`}
                      onClick={() => setMapMode("chances")}
                    >
                      Paikat
                    </button>
                    <button 
                      className={`control-btn ${mapMode === "efficiency" ? "active" : ""}`}
                      onClick={() => setMapMode("efficiency")}
                    >
                      Tehokkuus
                    </button>
                  </div>
                </div>

                <div className={`map-legend-container ${finalVizType === "markers" ? "visible" : "hidden"}`}>
                  <div className="map-legend">
                    <div className="legend-item">
                        <span className="legend-dot goal"></span>
                        <span>Maali</span>
                    </div>
                    <div className="legend-item">
                        <span className="legend-dot chance"></span>
                        <span>Maalipaikka</span>
                    </div>
                  </div>
                </div>
             </div>
          </div>

          <div className="player-map-wrapper net-map-large">
            <h3 className="player-map-title">Maalipaikat</h3>
            <PlayerNetMap 
              zoneStats={filteredData.net_zones} 
              markers={filteredData.net_markers}
              mode={mapMode === "kaikki" ? "chances_for" : (mapMode === "goals" ? "goals_for" : (mapMode === "chances" ? "chances_for_no_goals" : "efficiency_for"))}
              showMarkers={finalVizType === "markers"}
              showZones={finalVizType === "zones"}
            />
          </div>
        </div>
      </section>

      <div className="player-page-grid">
        <div className="player-page-column left-column">
           <ShotTypeTable 
             shotTypeStats={filteredData.shot_type_stats} 
             totalGoals={filteredData.summary.goals}
             totalChances={filteredData.summary.chances}
           />
           <PlayerSpiderChart 
             spiderData={playerData.spider_data}
             playerName={`${playerData.first_name} ${playerData.last_name}`}
           />
        </div>
        <div className="player-page-column right-column">
           <RollingAverageChart 
             trendData={filteredData.trend_data} 
             playerName={`${playerData.first_name} ${playerData.last_name}`}
             playerPosition={playerData.position}
           />
           <OnIceSynergyChart 
             synergyData={playerData.synergy_data}
           />
        </div>
        
        {/* Full width Bottom Section */}
        <ChemistrySection 
          chemistryData={playerData.chemistry_data}
        />
      </div>
    </ScrollContainer>
  );
}
