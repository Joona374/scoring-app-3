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
                <Link to="/tagging">Tilastoi</Link>
              </li>
              <li>
                <Link to="/excel-exporter">Excel-vienti</Link>
              </li>
              <li>
                <Link to="/roster-management">Kokoonpanon hallinta</Link>
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
