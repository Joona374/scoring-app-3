import { useNavigate } from "react-router-dom";
import "./PlayerHeader.css";

export default function PlayerHeader({ player }) {
  const navigate = useNavigate();

  if (!player) {
    return null;
  }

  // Position translation to Finnish if needed, but it seems it's already in Finnish from backend or can be mapped
  const positionMap = {
    "FORWARD": "Hyökkääjä",
    "DEFENDER": "Puolustaja",
    "GOALIE": "Maalivahti"
  };

  const displayPosition = positionMap[player.position] || player.position;
  const metaParts = [displayPosition, player.team_name].filter(Boolean);

  return (
    <header className="player-header">
      <div className="player-info-main">
        <h1 className="player-name">
          {player.first_name} {player.last_name}{" "}
          <span className="player-jersey-number-header">
            #{player.jersey_number}
          </span>
        </h1>
        {metaParts.length > 0 && (
          <p className="player-meta">{metaParts.join(" | ")}</p>
        )}
      </div>
      <button
        className="back-to-dashboard-btn"
        onClick={() => navigate("/dashboard")}
      >
        Joukkuesivulle
      </button>
    </header>
  );
}
