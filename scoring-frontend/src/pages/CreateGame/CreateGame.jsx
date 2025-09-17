import { useEffect, useState, useContext } from "react";
import { TaggingContext } from "../../context/TaggingContext";
import "./Styles/CreateGame.css";
import CreateGameForm from "./CreateGameForm";
import RosterSelector from "../../components/RosterSelector/RosterSelector";
import Modal from "../../components/Modal/Modal";
import MiniRosterView from "./MiniRosterView";
import MutedButton from "../../components/MutedButton/MutedButton";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function CreateGame({ pickMode, setCurrentGameId, onCancel }) {
  const { playersInTeam, fetchPlayersInTeam } = useContext(TaggingContext);

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
  const [powerplays, setPowerplays] = useState(null);
  const [penaltyKills, setPenaltyKills] = useState(null);
  const [showRosterSelector, setShowRosterSelector] = useState(false);
  const [playersInRoster, setPlayersInRoster] = useState(
    generateEmptyPlayersInRoster()
  );
  const [isLoadingCreateGame, setIsLoadingCreateGame] = useState(false);

  useEffect(() => {
    fetchPlayersInTeam();
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
          powerplays: powerplays,
          penalty_kills: penaltyKills,
        }),
      });

      if (!res.ok) {
        console.log("Failed to create game", res);
        setIsLoadingCreateGame(false);
      }

      const data = await res.json();
      setCurrentGameId(data.game_id);
      setIsLoadingCreateGame(false);
      pickMode();
    } catch (error) {
      setIsLoadingCreateGame(false);
      console.log("Failed to create game", error);
    }
  };

  const updateRoster = (newRoster) => {
    setPlayersInRoster(newRoster);
  };

  return (
    <div className="create-game-page">
      <h1>Luo uusi peli</h1>

      <div className="create-game-form-wrapper">
        <CreateGameForm
          opponent={opponent}
          setOpponent={setOpponent}
          setGameDate={setGameDate}
          setHomeGame={setHomeGame}
          setPowerplays={setPowerplays}
          setPenaltyKills={setPenaltyKills}
          powerplays={powerplays}
          penaltyKills={penaltyKills}
          showRosterSelector={showRosterSelector}
          setShowRosterSelector={setShowRosterSelector}
          submitGame={submitGame}
          isLoadingCreateGame={isLoadingCreateGame}
        />
        <MiniRosterView playersInRoster={playersInRoster} />
      </div>

      <MutedButton
        text="Peruuta"
        onClickMethod={() => onCancel()}
      ></MutedButton>

      {showRosterSelector && (
        <Modal
          children={
            <RosterSelector
              setShowRosterSelector={setShowRosterSelector}
              playersInTeam={playersInTeam}
              playersInRoster={playersInRoster}
              updateRoster={updateRoster}
            />
          }
        ></Modal>
      )}
    </div>
  );
}
