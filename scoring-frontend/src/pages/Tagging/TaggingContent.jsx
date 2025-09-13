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
    setGamesForTeam,
    currentTaggingMode,
    setCurrentTaggingMode,
    taggedEvents,
    setTaggedEvents,
    getGamesFromBackend,
  } = useContext(TaggingContext);
  const [view, setView] = useState("picker"); // Options: 'picker', 'create'

  useEffect(() => {
    getGamesFromBackend();
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
          setGamesForTeam={setGamesForTeam}
          setCurrentGameId={setCurrentGameId}
          onReturn={() => setView("picker")}
          fetchGamesForTeam={getGamesFromBackend}
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
