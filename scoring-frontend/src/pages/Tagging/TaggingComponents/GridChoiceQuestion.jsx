import { useContext } from "react";
import { TaggingContext } from "../../../context/TaggingContext";
import "../Styles/GridChoiceQuestion.css";
export default function GridChoiceQuestion() {
  const { currentTag, questionObjects, currentQuestionId, advanceQuestion } =
    useContext(TaggingContext);

  // Could this also be done in more DRY way?
  const currentQuestion = questionObjects.find(
    (q) => q.id === currentQuestionId
  );
  const questionKey = currentQuestion.key;
  const questionText = currentQuestion.text;
  const questionOptions = currentQuestion.options;

  const handleAnswerClick = (option, event) => {
    event.target.blur(); // Remove focus from the button
    const newTag = { ...currentTag, [questionKey]: option.answer };
    advanceQuestion(option.last_question, option.next_question_id, newTag);
  };

  return (
    <div className="grid-question-container">
      <h3 className="grid-question-text">{questionText}</h3>
      <div
        className={
          currentQuestion.options.length <= 1
            ? "grid-options single-grid-option"
            : "grid-options"
        }
      >
        {questionOptions.map((option, index) => {
          return (
            <button
              className="grid-option-button"
              onClick={(e) => handleAnswerClick(option, e)}
              key={index}
            >
              {option.answer_text}
            </button>
          );
        })}
      </div>
    </div>
  );
}
