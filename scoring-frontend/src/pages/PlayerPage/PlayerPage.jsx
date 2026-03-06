import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "./PlayerPage.css";
import LoadingSpinner from "../../components/LoadingSpinner/LoadingSpinner";
import ScrollContainer from "../../components/ScrollContainer/ScrollContainer";
import PlayerHeader from "./components/PlayerHeader";
import PlayerKPIs from "./components/PlayerKPIs";

export default function PlayerPage() {
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [playerData, setPlayerData] = useState(null);
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

  return (
    <ScrollContainer className="player-page-wrapper">
      <PlayerHeader player={playerData} />
      <PlayerKPIs summary={playerData.summary} />

      <div className="player-page-content">
        <p>Pelaajasivu työn alla...</p>
      </div>
    </ScrollContainer>
  );
}
