import { useContext } from "react";
import kaukalo from "../../assets/kaukalo.png";
import { TaggingContext } from "../../context/TaggingContext";

export default function TaggingArea() {
  const { currentTag, setCurrentTag, taggedEvents, setTaggedEvents } =
    useContext(TaggingContext);

  const handleImageClick = (event) => {
    const x = event.nativeEvent.offsetX;
    const y = event.nativeEvent.offsetY;

    const newTag = {
      ...currentTag,
      location: { x, y },
    };

    setCurrentTag(newTag);
    setTaggedEvents([...taggedEvents, newTag]);

    console.log("New currentTag:", newTag);
    console.log("All tagged events (incl. this):", [...taggedEvents, newTag]);

    // Optional reset
    setCurrentTag({});
  };

  return (
    <div>
      <h1>Tagging</h1>
      <img src={kaukalo} alt="Kaukalo" onClick={handleImageClick} />
    </div>
  );
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
