import { TaggingProvider } from "../../context/TaggingContext";
import TaggingArea from "./TaggingArea";
import TaggingSummary from "./TaggingSummary";
import "./Styles/Tagging.css";

export default function Tagging() {
  return (
    <TaggingProvider>
      <div className="tagging-page">
        <div className="left-column">
          <TaggingArea></TaggingArea>
        </div>
        <div className="right-column">
          <TaggingSummary></TaggingSummary>
        </div>
      </div>
    </TaggingProvider>
  );
}
