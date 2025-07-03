import "./Navbar.css";
import { useContext } from "react";
import AuthContext from "../../auth/AuthContext";
import { Link } from "react-router-dom";

export default function Navbar() {
  const { isLoggedIn } = useContext(AuthContext);

  return (
    <nav>
      <ul>
        <li>
          <Link to="/">Home</Link>
        </li>
        {!isLoggedIn ? (
          <>
            {" "}
            <li>
              <Link to="/register">Register</Link>
            </li>
            <li>
              <Link to="/login">Login</Link>
            </li>
            {/* TODO: PROTECT THIS IN PROD */}
            <li>
              <Link to="/admin">Admin</Link>
            </li>
          </>
        ) : (
          <>
            <li>
              <Link to="/dashboard">Dashboard</Link>
            </li>
            <li>
              <Link to="/create-team">Create a Team</Link>
            </li>
            <li>
              <Link to="/create-player">Create a Player</Link>
            </li>
            <li>
              <Link to="/create-game">Create a Game</Link>
            </li>
            <li>
              <Link to="/tagging">Tagging</Link>
            </li>
            <li>
              <Link to="/excel-test">Excel Test</Link>
            </li>
            <li>
              <Link to="/admin">Admin</Link>
            </li>
          </>
        )}
      </ul>
    </nav>
  );
}
