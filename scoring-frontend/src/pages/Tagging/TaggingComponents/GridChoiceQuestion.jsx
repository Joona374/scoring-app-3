import { useContext } from "react";
import { TaggingContext } from "../../../context/TaggingContext";

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

  const handleAnswerClick = (option) => {
    const newTag = { ...currentTag, [questionKey]: option.answer };

    advanceQuestion(option.last_question, option.next_question_id, newTag);
  };

  return (
    <>
      <p>{questionText}</p>
      {questionOptions.map((option, index) => {
        return (
          <div onClick={() => handleAnswerClick(option)} key={index}>
            {option.answer}
          </div>
        );
      })}
    </>
  );

  // AFTER ANSWER, CHECK IF IS LAST QUESTION, then reset currentQuestionId to firstQuestionId.
  // This should be done in some DRY way.
}
