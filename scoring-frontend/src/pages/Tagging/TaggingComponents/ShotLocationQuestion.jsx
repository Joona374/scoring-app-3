import { useContext } from "react";
import { TaggingContext } from "../../../context/TaggingContext";
import kaukalo from "../../../assets/kaukalo.png";
import "../Styles/ShotLocationQuestion.css";

export default function ShotLocationQuestion() {
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
      location: { x: percentageX, y: percentageY },
    };

    advanceQuestion(last_question, next_question_id, newTag);
  };

  return (
    <div className="kaukalo-image-container">
      <img
        src={kaukalo}
        alt="Kaukalo"
        className="kaukalo-image"
        onClick={handleImageClick}
      />
    </div>
  );
}
