import { useContext, useEffect } from "react";
import { TaggingContext } from "../../context/TaggingContext";
import ShotLocationQuestion from "./TaggingComponents/ShotLocationQuestion";
import GridChoiceQuestion from "./TaggingComponents/GridChoiceQuestion";
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
  } = useContext(TaggingContext);

  // Get the current question using the currentQuestionId
  const currentQuestion = questionObjects.find(
    (q) => q.id === currentQuestionId
  );

  // If no currentQuestion (still fecthing) display Loading...
  if (!currentQuestion) return <p>Loading...</p>;

  const renderQuestionComponent = () => {
    switch (currentQuestion.type) {
      case "SHOT LOCATION":
        return <ShotLocationQuestion question={currentQuestion} />;
      case "TEXT":
        return <GridChoiceQuestion question={currentQuestion} />;
      default:
        return <p>Unknow question type</p>;
    }
  };

  return <div className="question-container">{renderQuestionComponent()}</div>;
}

// TODO: MVP Question Flow
// - Fetch questions.json from backend on mount (useEffect)
// - Store questions and currentQuestionId in context or local state
// - Look up current question object by ID
// - Render question component based on type:
//     - SHOT_LOCATION -> <ShotLocationQuestion />
//     - TEXT          -> <TextQuestion />
// - Each question component calls `submitAnswer(value)` to:
//     - Save answer (optional)
//     - Update currentQuestionId to next_question_id
// - If final_question is true -> show "Done" or summary
