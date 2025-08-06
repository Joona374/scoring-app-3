import "./BasicButton.css";

export default function BasicButton({ text, onClickMethod }) {
  return (
    <button
      className="basic-button"
      onClick={() => {
        onClickMethod();
      }}
    >
      {text}
    </button>
  );
}
