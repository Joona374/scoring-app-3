import { useEffect, useState } from "react";
import "./Styles/CreateGame.css";
import CreateGameForm from "./CreateGameForm";
import RosterSelector from "./RosterSelector";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
const token = sessionStorage.getItem("jwt_token");
console.log(token);

export default function CreateGame() {
  const [opponent, setOpponent] = useState("");
  const [gameDate, setGameDate] = useState(null);
  const [homeGame, setHomeGame] = useState(null);
  const [showRosterSelector, setShowRosterSelector] = useState(false);
  const [players, setPlayers] = useState([]);

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/players/for-team`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) {
          throw new Error("Failed to fetch players for users teams");
        }

        const players = await res.json();
        console.log(players);
        setPlayers(players);
      } catch (error) {
        console.log("Error?: ", error);
        throw new Error("Failed to fetch players for users teams");
      }
    };

    fetchPlayers();
  }, []);

  const submitGame = (event) => {
    event.preventDefault();
    console.log(opponent);
  };

  return (
    <>
      <CreateGameForm
        opponent={opponent}
        setOpponent={setOpponent}
        setGameDate={setGameDate}
        setHomeGame={setHomeGame}
        setShowRosterSelector={setShowRosterSelector}
        submitGame={submitGame}
      />
      {showRosterSelector && (
        <RosterSelector
          setShowRosterSelector={setShowRosterSelector}
          players={players}
        />
      )}
    </>
  );
}
