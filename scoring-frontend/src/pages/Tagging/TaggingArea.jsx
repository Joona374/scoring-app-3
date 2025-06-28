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
