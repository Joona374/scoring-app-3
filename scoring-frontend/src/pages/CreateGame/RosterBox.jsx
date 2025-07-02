export default function RosterBox({
  id,
  selectingPosition,
  setSelectingPosition,
}) {
  const handleRosterBoxClick = (target) => {
    if (target.id !== selectingPosition) {
      console.log("Selected:", target.id);
      setSelectingPosition(target.id);
    } else {
      setSelectingPosition("");
      console.log("Already selected");
      target.className = "player-in-roster-box";
    }
  };

  return (
    <div
      id={id}
      className={`player-in-roster-box ${
        selectingPosition === id ? "active" : ""
      }`}
      onClick={(event) => handleRosterBoxClick(event.target)}
    >
      {id}
    </div>
  );
}
