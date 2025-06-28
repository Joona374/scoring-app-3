import { TaggingProvider } from "../../context/TaggingContext";
import TaggingArea from "./TaggingArea";

export default function Tagging() {
  return (
    <TaggingProvider>
      <TaggingArea></TaggingArea>
    </TaggingProvider>
  );
}
