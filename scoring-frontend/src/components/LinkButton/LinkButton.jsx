import "./LinkButton.css";
import { Link } from "react-router-dom";

export default function LinkButton({ text, path }) {
  return (
    <div className="button-wrapper">
      <Link className="link-button" to={path}>
        {text}
      </Link>
    </div>
  );
}
