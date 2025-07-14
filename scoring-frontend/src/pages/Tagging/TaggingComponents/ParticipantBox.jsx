import "../Styles/ParticipantBox.css";

export default function ParticipantBox({
  player,
  clickHandler,
  participants,
  onIces,
  currentTag,
  setCurrentTag,
  prevTag,
  advanceQuestion,
  question,
}) {
  const clicker = () => {
    if (player) {
      const new_tag = { ...prevTag, shooter: player };
      advanceQuestion(false, question.next_question_id, new_tag);
    }
  };

  let playersName;
  if (player) {
    playersName = `${player.first_name} ${player.last_name}`;
  } else playersName = "--";

  // Determine color scheme based on currentTag
  let colorClass = "";
  if (
    currentTag &&
    (currentTag.shot_result === "Maali +" || currentTag.shot_result === "MP +")
  ) {
    colorClass = "green";
  } else if (
    currentTag &&
    (currentTag.shot_result === "Maali -" || currentTag.shot_result === "MP -")
  ) {
    colorClass = "red";
  }

  let className = "participant-box";
  if (player) {
    if (participants.includes(player.id))
      className = `participant-box participated ${colorClass}`;
    else if (onIces.includes(player.id))
      className = `participant-box on-ice ${colorClass}`;
  }

  return (
    <button
      className={className}
      onClick={() => {
        clickHandler(player);
      }}
    >
      {playersName}
    </button>
  );
}
