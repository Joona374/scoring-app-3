import "./TwoColumnLayout.css";

export default function TwoColumnLayout({ left, right }) {
  return (
    <div className="two-column-layout">
      <div className="left-column">{left}</div>
      <div className="separator"></div>
      <div className="right-column">{right}</div>
    </div>
  );
}
