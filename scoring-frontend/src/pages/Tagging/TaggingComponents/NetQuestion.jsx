import { useContext } from "react";
import { TaggingContext } from "../../../context/TaggingContext";
import maali from "../../../assets/maali.jpg";
import "../Styles/ShotLocationQuestion.css";

export default function NetQuestion() {
  const { currentTag, questionObjects, currentQuestionId, advanceQuestion } =
    useContext(TaggingContext);

  // Get the current question using the currentQuestionId
  const currentQuestion = questionObjects.find(
    (q) => q.id === currentQuestionId
  );

  const handleImageClick = (event) => {
    const img = event.target;

    const x = event.nativeEvent.offsetX;
    const imageWidth = img.offsetWidth;
    const percentageX = Math.round((x / imageWidth) * 100);

    const y = event.nativeEvent.offsetY;
    const imageHeight = img.offsetHeight;
    const percentageY = Math.round((y / imageHeight) * 100);

    const last_question = currentQuestion.last_question;
    const next_question_id = currentQuestion.next_question_id;
    const newTag = {
      ...currentTag,
      net: { x: percentageX, y: percentageY },
    };

    advanceQuestion(last_question, next_question_id, newTag);
  };

  return (
    <div className="kaukalo-image-container">
      <img
        src={maali}
        alt="maali"
        className="kaukalo-image"
        onClick={handleImageClick}
      />
    </div>
  );
}
