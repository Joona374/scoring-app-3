import "../Styles/PlayerBox.css";

export default function PlayerBox({
  name,
  pos,
  player,
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

  const posClass = pos === "FORWARD" ? "forward" : "defense";

  return (
    <button className={`player-box-btn ${posClass}`} onClick={clicker}>
      {name}
    </button>
  );
}
