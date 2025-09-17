import { useContext, useEffect, useState } from "react";
import { TaggingContext } from "../../context/TaggingContext";

import ShotLocationQuestion from "./TaggingComponents/ShotLocationQuestion";
import GridChoiceQuestion from "./TaggingComponents/GridChoiceQuestion";
import ShooterQuestion from "./TaggingComponents/ShooterQuestion";
import CreateGame from "../CreateGame/CreateGame";
import "./Styles/TaggingArea.css";
import GamePicker from "./GamePicker";
import ContinueGamePicker from "./ContinueGamePicker";
import NetQuestion from "./TaggingComponents/NetQuestion";
import ParticapntsQuestion from "./TaggingComponents/ParticipantsQuestion";

export default function TaggingArea() {
  // Import the "public" variables from context
  const {
    currentTag,
    setCurrentTag,
    taggedEvents,
    setTaggedEvents,
    questionObjects,
    setQuestionObjects,
    currentQuestionId,
    setCurrentQuestionId,
    playersInRoster,
    setPlayersInRoster,
    currentGameId,
    setCurrentGameId,
    gamesForTeam,
    setGamesForTeam,
  } = useContext(TaggingContext);

  // This function gets the roster for this game form db
  const getRosterFromDb = async (gameId) => {
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
    const token = sessionStorage.getItem("jwt_token");

    try {
      const res = await fetch(
        `${BACKEND_URL}/tagging/roster-for-game?game_id=${gameId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!res.ok) {
        console.log("Error fetching roster for game:", gameId);
      }

      const data = await res.json();
      setPlayersInRoster(data);
    } catch (err) {
      console.log(err);
    }
  };

  useEffect(() => {
    if (currentGameId) getRosterFromDb(currentGameId);
  }, [currentGameId]);

  // Get the current question using the currentQuestionId
  const currentQuestion = questionObjects.find(
    (q) => q.id === currentQuestionId
  );

  if (!currentGameId) {
    if (view === "picker") {
      return (
        <GamePicker
          setCurrentGameId={setCurrentGameId}
          onCreateGame={() => setView("create")}
          onContinueGame={() => setView("continue")}
        />
      );
    } else if (view === "create") {
      return (
        <CreateGame
          setCurrentGameId={setCurrentGameId}
          onCancel={() => setView("picker")}
        />
      );
    } else {
      return (
        <ContinueGamePicker
          gamesForTeam={gamesForTeam}
          setCurrentGameId={setCurrentGameId}
        ></ContinueGamePicker>
      );
    }
  }

  // If no currentQuestion (still fecthing) display Loading...
  if (!currentQuestion) return <p>Loading...</p>;

  const renderQuestionComponent = () => {
    switch (currentQuestion.type) {
      case "SHOT LOCATION":
        return <ShotLocationQuestion />;
      case "NET LOCATION":
        return <NetQuestion />;
      case "TEXT":
        return <GridChoiceQuestion />;
      case "SHOOTER":
        return <ShooterQuestion />;
      case "PARTICIPANTS":
        return <ParticapntsQuestion />;
      default:
        return <p>Unknow question type</p>;
    }
  };

  return <div className="question-container">{renderQuestionComponent()}</div>;
}
