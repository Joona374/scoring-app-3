import { useEffect, useState } from "react";
import "../../components/FormStyles.css";
import TwoColumnLayout from "../../components/TwoColumnLayout/TwoColumnLayout";
import CreatePlayer from "./CreatePlayer";
import UpdatePlayer from "./EditPlayer";
import "./RosterManagement.css";

export default function RosterManagement() {
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

        if (!response.ok) throw new Error("Failed to fetch user info");

        const data = await response.json();
        setPlayers(data);
      } catch (err) {
        console.log("Error:", err);
      }
    };

    getPlayers();
  }, []);

  const editPlayer = (player) => {
    setPlayerToEdit(player);
    setLeftColumnState("edit");
  };

  const renderLeftContent = () => {
    if (leftColumnState === "create") {
      return <CreatePlayer players={players} setPlayers={setPlayers} />;
    }
    if (leftColumnState === "edit") {
      return (
        <UpdatePlayer
          players={players}
          setPlayers={setPlayers}
          player={playerToEdit}
        />
      );
    }
    return (
      <form className="auth-form">
        <div className="form-title">Kokoonpanon hallinta</div>
      </form>
    );
  };

  const renderRightContent = () => (
    <>
      <button
        className="add-player-btn"
        onClick={() => setLeftColumnState("create")}
      >
        + Lisää uusi pelaaja
      </button>

      <div className="player-sections-scroll">
        {["Hyökkääjät", "Puolustajat", "Maalivahdit"].map((section) => (
          <div key={section} className="player-section">
            <h2>{section}</h2>
            {players.map((player, idx) => {
              const posMatch =
                (section === "Hyökkääjät" &&
                  (player.position === "FORWARD" ||
                    player.position === "Hyökkääjä")) ||
                (section === "Puolustajat" &&
                  (player.position === "DEFENDER" ||
                    player.position === "Puolustaja")) ||
                (section === "Maalivahdit" &&
                  (player.position === "GOALIE" ||
                    player.position === "Maalivahti"));

              if (posMatch) {
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
              return null;
            })}
          </div>
        ))}
      </div>
    </>
  );

  return (
    <TwoColumnLayout left={renderLeftContent()} right={renderRightContent()} />
  );
}
