import { useContext } from "react";
import "./Styles/TaggingSummary.css";
import { TaggingContext } from "../../context/TaggingContext";

export default function TaggingSummary() {
  const { taggedEvents } = useContext(TaggingContext);
  return (
    <>
      <h3>Tagging summary</h3>
      {taggedEvents.map((tag, index) => {
        return (
          <p className="listTag">
            {index + 1}. {tag.shot_result} {tag.shot_type}
          </p>
        );
      })}
    </>
  );
}
