import "../Styles/ParticipantBox.css";

export default function ParticipantBox({
  player,
  clickHandler,
  participants,
  onIces,
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

  let className = "participant-box";

  if (player) {
    if (participants.includes(player.id))
      className = "participant-box participated";
    else if (onIces.includes(player.id)) className = "participant-box on-ice";
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
