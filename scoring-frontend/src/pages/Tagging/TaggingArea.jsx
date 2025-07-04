import { useContext, useEffect } from "react";
import { TaggingContext } from "../../context/TaggingContext";

import ShotLocationQuestion from "./TaggingComponents/ShotLocationQuestion";
import GridChoiceQuestion from "./TaggingComponents/GridChoiceQuestion";
import ShooterQuestion from "./TaggingComponents/ShooterQuestion";
import "./Styles/TaggingArea.css";

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
        console.log(
          "no work getting roster for game (IS IT 1? Forgot to change?):",
          gameId
        );
      }

      const data = await res.json();
      console.log(data);
      setPlayersInRoster(data);
    } catch (err) {
      console.log(err);
    }
  };

  useEffect(() => {
    // HARDOCED JUST FOR NOW TESTING TODO CHANGE!!
    const gameId = 1;
    getRosterFromDb(gameId);
  }, []);

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
      case "TEXT":
        return <GridChoiceQuestion />;
      case "SHOOTER":
        return <ShooterQuestion />;
      default:
        return <p>Unknow question type</p>;
    }
  };

  return <div className="question-container">{renderQuestionComponent()}</div>;
}

// TODO: MVP Question Flow
// - Render question component based on type:
//     - SHOT_LOCATION -> <ShotLocationQuestion />
//     - TEXT          -> <TextQuestion />
// - Each question component calls `submitAnswer(value)` to:
//     - Save answer (optional)
//     - Update currentQuestionId to next_question_id
// - If final_question is true -> show "Done" or summary
