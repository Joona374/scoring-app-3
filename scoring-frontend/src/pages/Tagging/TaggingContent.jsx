import TaggingArea from "./TaggingArea";
import GamePicker from "./GamePicker";
import CreateGame from "../CreateGame/CreateGame";
import ContinueGamePicker from "./ContinueGamePicker";
import TaggingModePicker from "./TaggingModePicker";

PlayerStatsMode;

import { useContext, useEffect, useState } from "react";
import { TaggingContext } from "../../context/TaggingContext";
import "./Styles/Tagging.css";
import PlayerStatsMode from "./PlayerStatsMode";
import GoalieStatsMode from "./GoalieStatsMode";
import TeamStatsMode from "./TeamStatsMode";

export default function Tagging() {
  const {
    currentGameId,
    setCurrentGameId,
    gamesForTeam,
    setGamesForTEam,
    currentTaggingMode,
    setCurrentTaggingMode,
    taggedEvents,
    setTaggedEvents,
  } = useContext(TaggingContext);
  const [view, setView] = useState("picker"); // Options: 'picker', 'create'

  useEffect(() => {
    const getGames = async () => {
      const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
      const token = sessionStorage.getItem("jwt_token");

      try {
        const res = await fetch(`${BACKEND_URL}/games/get-for-user`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) {
          console.log(
            "Getting a list of games to continue from the server failed."
          );
        }

        const data = await res.json();
        setGamesForTEam(data);
      } catch (err) {
        console.log(err);
      }
    };

    getGames();
  }, []);

  if (!currentGameId || !currentTaggingMode) {
    if (view === "picker") {
      return (
        <div className="game-picker-container">
          <GamePicker
            setCurrentGameId={setCurrentGameId}
            onCreateGame={() => setView("create")}
            onContinueGame={() => setView("continue")}
          />
        </div>
      );
    } else if (view === "create") {
      return (
        <CreateGame
          pickMode={() => setView("mode")}
          setCurrentGameId={setCurrentGameId}
          onCancel={() => setView("picker")}
        />
      );
    } else if (view === "continue") {
      return (
        <ContinueGamePicker
          pickMode={() => setView("mode")}
          gamesForTeam={gamesForTeam}
          setCurrentGameId={setCurrentGameId}
          onReturn={() => setView("picker")}
        ></ContinueGamePicker>
      );
    } else if (view === "mode") {
      return (
        <TaggingModePicker
          setCurrentTaggingMode={setCurrentTaggingMode}
          onReturn={() => setView("picker")}
        ></TaggingModePicker>
      );
    }
  }

  if (currentTaggingMode === "team") {
    return <TeamStatsMode></TeamStatsMode>;
  } else if (currentTaggingMode === "player") {
    return (
      <PlayerStatsMode
        currentGameId={currentGameId}
        setTaggedEvents={setTaggedEvents}
        taggedEvents={taggedEvents}
      ></PlayerStatsMode>
    );
  } else if (currentTaggingMode === "goalie") {
    return (
      <GoalieStatsMode
        returnMethod={() => setCurrentTaggingMode("")}
      ></GoalieStatsMode>
    );
  }
}
