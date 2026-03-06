import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "./PlayerPage.css";
import LoadingSpinner from "../../components/LoadingSpinner/LoadingSpinner";
import ScrollContainer from "../../components/ScrollContainer/ScrollContainer";
import PlayerHeader from "./components/PlayerHeader";
import PlayerKPIs from "./components/PlayerKPIs";
import PlayerIceMap from "./components/PlayerIceMap";
import PlayerNetMap from "./components/PlayerNetMap";

export default function PlayerPage() {
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [playerData, setPlayerData] = useState(null);
  
  // mapMode: kaikki, goals, chances, efficiency
  const [mapMode, setMapMode] = useState("kaikki"); 
  // vizType: markers (Paikoittain), zones (Alueittain)
  const [vizType, setVizType] = useState("markers"); 
  
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
          if (response.status === 404) {
             throw new Error("Pelaajaa ei löytynyt");
          }
          if (response.status === 403) {
             throw new Error("Ei oikeutta pelaajan tietoihin");
          }
          throw new Error("Virhe tietojen haussa");
        }

        const data = await response.json();
        setPlayerData(data);
      } catch (err) {
        console.error("PlayerPage error:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPlayerStats();
  }, [id]);

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

  // Filter markers and zones based on mapMode
  const getFilteredData = () => {
    if (!playerData) return { ice_zones: {}, net_zones: {}, ice_markers: [], net_markers: [] };

    let ice_markers = playerData.ice_markers;
    let net_markers = playerData.net_markers;
    let ice_zones = { ...playerData.ice_zones };
    let net_zones = { ...playerData.net_zones };

    if (mapMode === "goals") {
      ice_markers = ice_markers.filter(m => m.result === "Maali +");
      net_markers = net_markers.filter(m => m.result === "Maali +");
      // For zones, we only care about goals_for in this mode
    } else if (mapMode === "chances") {
      ice_markers = ice_markers.filter(m => m.result !== "Maali +");
      net_markers = net_markers.filter(m => m.result !== "Maali +");
    }

    return { ice_zones, net_zones, ice_markers, net_markers };
  };

  const filteredData = getFilteredData();

  return (
    <ScrollContainer className="player-page-wrapper">
      <PlayerHeader player={playerData} />
      <PlayerKPIs summary={playerData.summary} />

      {/* Visualizations Section */}
      <section className="player-visualizations-section">
        <div className="player-visualizations-grid">
          <div className="player-map-wrapper ice-map-large">
            <h3 className="player-map-title">Laukaisupaikat</h3>
            <PlayerIceMap 
              zoneStats={filteredData.ice_zones} 
              markers={filteredData.ice_markers}
              mode={mapMode === "kaikki" ? "chances_for" : (mapMode === "goals" ? "goals_for" : (mapMode === "chances" ? "chances_for_no_goals" : "efficiency_for"))}
              showMarkers={vizType === "markers"}
              showZones={vizType === "zones"}
            />
          </div>

          <div className="player-map-controls-wrapper">
             <div className="player-map-controls">
                <div className="control-group">
                  <span className="control-label">Näkymä</span>
                  <div className="viz-type-toggle">
                    <button 
                      className={`toggle-btn ${vizType === "markers" ? "active" : ""}`}
                      onClick={() => setVizType("markers")}
                    >
                      Paikoittain
                    </button>
                    <button 
                      className={`toggle-btn ${vizType === "zones" ? "active" : ""}`}
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

          <div className="player-map-wrapper net-map-large">
            <h3 className="player-map-title">Maalipaikat</h3>
            <PlayerNetMap 
              zoneStats={filteredData.net_zones} 
              markers={filteredData.net_markers}
              mode={mapMode === "kaikki" ? "chances_for" : (mapMode === "goals" ? "goals_for" : (mapMode === "chances" ? "chances_for_no_goals" : "efficiency_for"))}
              showMarkers={vizType === "markers"}
              showZones={vizType === "zones"}
            />
          </div>
        </div>
      </section>

      <div className="player-page-grid">
        <div className="player-page-column left-column">
           <div className="placeholder-card">
              <p>Lisää tilastoja tulossa (vasen)...</p>
           </div>
        </div>
        <div className="player-page-column right-column">
           <div className="placeholder-card">
              <p>Lisää tilastoja tulossa (oikea)...</p>
           </div>
        </div>
      </div>
    </ScrollContainer>
  );
}
