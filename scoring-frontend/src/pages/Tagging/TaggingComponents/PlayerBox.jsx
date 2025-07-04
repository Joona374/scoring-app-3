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
  let width;
  if (pos === "FORWARD") {
    width = "30%";
  } else {
    width = "46%";
  }
  return (
    <button
      style={{
        padding: "8px 16px",
        margin: "5px",
        width: width,
        borderRadius: "6px",
        border: "1px solid #007bff",
        background: "#007bff",
        color: "#fff",
        cursor: "pointer",
        fontSize: "16px",
        fontWeight: "bold",
        transition: "background 0.2s",
      }}
      onClick={() => {
        clicker();
      }}
    >
      {name}
    </button>
  );
}
