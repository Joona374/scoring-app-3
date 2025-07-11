import "./Navbar.css";
import { useContext } from "react";
import AuthContext from "../../auth/AuthContext";
import { Link } from "react-router-dom";

export default function Navbar() {
  const { isLoggedIn } = useContext(AuthContext);

  return (
    <nav>
      <div className="navbar-left">
        <Link to="/" style={{ color: "inherit", textDecoration: "none" }}>
          ScoringApp 3.0
        </Link>
      </div>

      <div className="navbar-right">
        <ul>
          {!isLoggedIn ? (
            <>
              <li>
                <Link to="/login">Kirjaudu</Link>
              </li>
              <li>
                <Link to="/register">Rekisteröidy</Link>
              </li>

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
                <Link to="/create-team">Luo joukkue</Link>
              </li>
              <li>
                <Link to="/create-player">Luo pelaaja</Link>
              </li>
              <li>
                <Link to="/create-game">Luo ottelu</Link>
              </li>
              <li>
                <Link to="/tagging">Merkintä</Link>
              </li>
              <li>
                <Link to="/excel-test">Excel-testi</Link>
              </li>
              <li>
                <Link to="/admin">Admin</Link>
              </li>
            </>
          )}
        </ul>
      </div>
    </nav>
  );
}
