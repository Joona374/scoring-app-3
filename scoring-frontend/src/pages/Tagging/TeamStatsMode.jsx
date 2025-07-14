import { useContext, useEffect, useState } from "react";
import { TaggingContext } from "../../context/TaggingContext";

import ShotLocationQuestion from "./TaggingComponents/ShotLocationQuestion";
import GridChoiceQuestion from "./TaggingComponents/GridChoiceQuestion";
import ShooterQuestion from "./TaggingComponents/ShooterQuestion";
import "./Styles/TaggingArea.css";
import NetQuestion from "./TaggingComponents/NetQuestion";
import ParticapntsQuestion from "./TaggingComponents/ParticipantsQuestion";
import TeamTaggingSummary from "./TeamTaggingSummary";

import { Question } from "./question";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function TeamStatsMode() {
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
    setGamesForTEam,
    setFirstQuestionId,
    stepBackInTag,
  } = useContext(TaggingContext);

  useEffect(() => {
    async function fetchQuestions() {
      const token = sessionStorage.getItem("jwt_token");

      try {
        const res = await fetch(`${BACKEND_URL}/tagging/questions/team`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        const questionsJson = await res.json();
        const questionObjs = questionsJson.questions.map(
          (element) => new Question(element)
        );
        setQuestionObjects(questionObjs);
        if (questionObjs.length > 0) {
          // TODO: CHANGING THIS BACK TO questionObjs[0]. This is just for dev
          setCurrentQuestionId(questionObjs[0].id);
          setFirstQuestionId(questionObjs[0].id);
        }
      } catch (err) {
        console.error("Error fetching questions from backend:", err);
      }
    }
    fetchQuestions();
  }, []);

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
        console.log(
          "no work getting roster for game (IS IT 1? Forgot to change?):",
          gameId
        );
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

  return (
    <div className="tagging-page">
      <div className="tagging-area-column">
        {renderQuestionComponent()}{" "}
        <button className={"tagging-back-button"} onClick={stepBackInTag}>
          {"<="}
        </button>{" "}
      </div>
      <div className="tagging-summary-column">
        <TeamTaggingSummary></TeamTaggingSummary>
      </div>
    </div>
  );
}
