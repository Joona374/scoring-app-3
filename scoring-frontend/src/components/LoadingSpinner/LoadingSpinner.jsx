import "./LoadingSpinner.css";

export default function LoadingSpinner(size) {
  return (
    <span
      className="spinner"
      style={{
        width: `${size}px`,
        height: `${size}px`,
        display: "inline-block",
      }}
    ></span>
  );
}
