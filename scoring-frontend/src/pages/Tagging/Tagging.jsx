import { TaggingProvider } from "../../context/TaggingContext";
import TaggingContent from "./TaggingContent";
import "./Styles/Tagging.css";

export default function Tagging() {
  return (
    <TaggingProvider>
      <TaggingContent />
    </TaggingProvider>
  );
}
