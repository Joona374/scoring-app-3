import { useEffect, useState } from "react";
import "./Styles/CreateGame.css";
import CreateGameForm from "./CreateGameForm";
import RosterSelector from "./RosterSelector";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function CreateGame({ setCurrentGameId, onCancel }) {
  console.log("CreateGame received setCurrentGameId:", typeof setCurrentGameId);
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
        console.log("OH NO ERROR INSIDE THE THING :D", res);
      }

      const data = await res.json();
      console.log("It went okay?", data);
      setCurrentGameId(data.game_id);
    } catch (error) {
      console.log("OH NO ERROR: ", error);
    }
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
          playersInRoster={playersInRoster}
          setPlayersInRoster={setPlayersInRoster}
        />
      )}
    </>
  );
}
