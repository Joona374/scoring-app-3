import { useEffect, useState } from "react";
import "./Styles/CreateGame.css";
import CreateGameForm from "./CreateGameForm";
import RosterSelector from "./RosterSelector";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function CreateGame({ pickMode, setCurrentGameId, onCancel }) {
  const generateEmptyPlayersInRoster = () => {
    let emptyPlayersInRoster = [];
    for (let i = 1; i <= 5; i++) {
      ["LW", "C", "RW"].map((position) =>
        emptyPlayersInRoster.push({ line: i, position: position, player: null })
      );
    }
    for (let i = 1; i <= 4; i++) {
      ["LD", "RD"].map((position) =>
        emptyPlayersInRoster.push({ line: i, position: position, player: null })
      );
    }
    for (let i = 1; i <= 2; i++) {
      ["G"].map((position) =>
        emptyPlayersInRoster.push({ line: i, position: position, player: null })
      );
    }

    return emptyPlayersInRoster;
  };

  const [opponent, setOpponent] = useState("");
  const [gameDate, setGameDate] = useState(null);
  const [homeGame, setHomeGame] = useState(null);
  const [showRosterSelector, setShowRosterSelector] = useState(false);
  const [players, setPlayers] = useState([]);
  const [playersInRoster, setPlayersInRoster] = useState(
    generateEmptyPlayersInRoster()
  );
  const [isLoadingCreateGame, setIsLoadingCreateGame] = useState(false);

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const token = sessionStorage.getItem("jwt_token");
        const res = await fetch(`${BACKEND_URL}/players/for-team`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) {
          throw new Error("Failed to fetch players for users teams");
        }

        const players = await res.json();
        setPlayers(players);
      } catch (error) {
        console.log("Error?: ", error);
        throw new Error("Failed to fetch players for users teams");
      }
    };

    fetchPlayers();
  }, []);

  const submitGame = async (event) => {
    event.preventDefault();
    setIsLoadingCreateGame(true);

    const token = sessionStorage.getItem("jwt_token");

    try {
      const res = await fetch(`${BACKEND_URL}/games/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          opponent,
          game_date: gameDate,
          home_game: homeGame,
          players_in_roster: playersInRoster,
        }),
      });

      if (!res.ok) {
        console.log("Failed to create game", res);
        setIsLoadingCreateGame(false);
      }

      const data = await res.json();
      console.log("It went okay?", data);
      setCurrentGameId(data.game_id);
      setIsLoadingCreateGame(false);
      pickMode();
    } catch (error) {
      setIsLoadingCreateGame(false);
      console.log("Failed to create game", error);
    }
  };

  return (
    <div className="create-game-page">
      <div className="create-game-form-wrapper">
        <h1>Luo uusi peli</h1>

        <CreateGameForm
          opponent={opponent}
          setOpponent={setOpponent}
          setGameDate={setGameDate}
          setHomeGame={setHomeGame}
          showRosterSelector={showRosterSelector}
          setShowRosterSelector={setShowRosterSelector}
          submitGame={submitGame}
          onCancel={onCancel}
          isLoadingCreateGame={isLoadingCreateGame}
          setIsLoadingCreateGame={setIsLoadingCreateGame}
        />
      </div>
      {showRosterSelector && (
        <RosterSelector
          setShowRosterSelector={setShowRosterSelector}
          players={players}
          playersInRoster={playersInRoster}
          setPlayersInRoster={setPlayersInRoster}
        />
      )}
    </div>
  );
}
