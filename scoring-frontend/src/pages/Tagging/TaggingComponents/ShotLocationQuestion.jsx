// const handleImageClick = (event) => {
//   const x = event.nativeEvent.offsetX;
//   const y = event.nativeEvent.offsetY;

//   const newTag = {
//     ...currentTag,
//     location: { x, y },
//   };

//   setCurrentTag(newTag);
//   setTaggedEvents([...taggedEvents, newTag]);

//   console.log("New currentTag:", newTag);
//   console.log("All tagged events (incl. this):", [...taggedEvents, newTag]);

//   // Optional reset
//   setCurrentTag({});
//   console.log(questionObjects);
// };
import kaukalo from "../../../assets/kaukalo.png";
import "../Styles/ShotLocationQuestion.css";

export default function ShotLocationQuestion() {
  const handleImageClick = (event) => {
    console.log("Image clicked");
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
