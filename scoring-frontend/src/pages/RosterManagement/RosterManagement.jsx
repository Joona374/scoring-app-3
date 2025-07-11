import { useEffect, useState } from "react";
import "../../components/FormStyles.css";
import "./RosterManagement.css";
import CreatePlayer from "./CreatePlayer";
import UpdatePlayer from "./EditPlayer";

export default function RosterManagement() {
  // Placeholder for later: players from backend
  const [players, setPlayers] = useState([]);
  const [leftColumnState, setLeftColumnState] = useState("");
  const [playerToEdit, setPlayerToEdit] = useState(null);

  useEffect(() => {
    const token = sessionStorage.getItem("jwt_token");
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

    const getPlayers = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/players/for-team`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch user info");
        }

        const data = await response.json();
        setPlayers(data);
        console.log(data);
      } catch (err) {
        console.log("Error:", err);
      }
    };

    getPlayers();
  }, []);

  const editPlayer = (player) => {
    console.log("This should edit player", player);
    setPlayerToEdit(player);
    setLeftColumnState(null);
    setLeftColumnState("edit");
  };

  return (
    <div className="roster-page">
      {/* Left column: Player editor */}
      <div className="player-editor">
        {leftColumnState === "create" ? (
          <CreatePlayer
            players={players}
            setPlayers={setPlayers}
          ></CreatePlayer>
        ) : leftColumnState === "edit" ? (
          <UpdatePlayer
            players={players}
            setPlayers={setPlayers}
            player={playerToEdit}
          ></UpdatePlayer>
        ) : (
          <form className="auth-form">
            <div className="form-title">Kokoonpanon hallinta</div>
          </form>
        )}
      </div>

      {/* Vertical separator */}
      <div className="separator"></div>

      {/* Right column: Player list */}
      <div className="player-list">
        <button
          className="add-player-btn"
          onClick={() => setLeftColumnState("create")}
        >
          + Lisää uusi pelaaja
        </button>

        <div className="player-sections-scroll">
          <div className="player-section">
            <h2>Hyökkääjät</h2>
            {players.map((player, idx) => {
              if (
                player.position == "FORWARD" ||
                player.position == "Hyökkääjä"
              ) {
                return (
                  <div
                    key={idx}
                    className="player-item"
                    onClick={() => editPlayer(player)}
                  >
                    {player.first_name} {player.last_name}
                  </div>
                );
              }
            })}
          </div>

          <div className="player-section">
            <h2>Puolustajat</h2>
            {players.map((player, idx) => {
              if (
                player.position == "DEFENDER" ||
                player.position == "Puolustaja"
              ) {
                return (
                  <div
                    key={idx}
                    className="player-item"
                    onClick={() => editPlayer(player)}
                  >
                    {player.first_name} {player.last_name}
                  </div>
                );
              }
            })}
          </div>

          <div className="player-section">
            <h2>Maalivahdit</h2>
            {players.map((player, idx) => {
              if (
                player.position == "GOALIE" ||
                player.position == "Maalivahti"
              ) {
                return (
                  <div
                    key={idx}
                    className="player-item"
                    onClick={() => editPlayer(player)}
                  >
                    {player.first_name} {player.last_name}
                  </div>
                );
              }
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
