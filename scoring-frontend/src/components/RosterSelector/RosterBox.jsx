export default function RosterBox({
  id,
  player,
  selectingPosition,
  setSelectingPosition,
  removePlayerFromRosterspot,
}) {
  const handleRosterBoxClick = (target) => {
    if (target.id !== selectingPosition) {
      setSelectingPosition(target.id);
    } else {
      setSelectingPosition("");
      target.className = "player-in-roster-box";
    }
  };

  const clickX = (rosterBoxId) => {
    removePlayerFromRosterspot(rosterBoxId);
  };

  return (
    <div
      id={id}
      className={`player-in-roster-box ${
        selectingPosition === id ? "active" : ""
      }`}
      onClick={(event) => handleRosterBoxClick(event.target)}
    >
      {player ? `${player.first_name} ${player.last_name}` : id}
      {player && (
        <button className={"roster-box-x"} onClick={() => clickX(id)}>
          X
        </button>
      )}
    </div>
  );
}
