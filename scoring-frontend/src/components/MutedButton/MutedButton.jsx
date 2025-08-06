import "./MutedButton.css";

export default function MutedButton({ text, onClickMethod }) {
  return (
    <button
      className="muted-button"
      onClick={() => {
        onClickMethod();
      }}
    >
      {text}
    </button>
  );
}
