import "./Navbar.css";
import { useContext, useState } from "react";
import AuthContext from "../../auth/AuthContext";
import { Link } from "react-router-dom";

export default function Navbar() {
  const { isLoggedIn, isAdmin } = useContext(AuthContext);
  const [menuOpen, setMenuOpen] = useState(false);

  const toggleMenu = () => setMenuOpen((prev) => !prev);

  return (
    <nav>
      <div className="navbar-left">
        <Link
          to="/"
          onClick={() => setMenuOpen(false)}
          style={{ color: "inherit", textDecoration: "none" }}
        >
          ScoringApp 3.0
        </Link>
      </div>

      <div className="hamburger" onClick={toggleMenu}>
        ☰
      </div>

      <div className={`navbar-right ${menuOpen ? "open" : ""}`}>
        <ul>
          {!isLoggedIn ? (
            <>
              <li>
                <Link onClick={() => setMenuOpen(false)} to="/login">
                  Kirjaudu
                </Link>
              </li>
              <li>
                <Link onClick={() => setMenuOpen(false)} to="/register">
                  Rekisteröidy
                </Link>
              </li>
            </>
          ) : (
            <>
              <li>
                <Link onClick={() => setMenuOpen(false)} to="/dashboard">
                  Joukkuesivu
                </Link>
              </li>
              <li>
                <Link onClick={() => setMenuOpen(false)} to="/tagging">
                  Tilastointi
                </Link>
              </li>
              <li>
                <Link onClick={() => setMenuOpen(false)} to="/excel-exporter">
                  Excel-vienti
                </Link>
              </li>
              <li>
                <Link
                  onClick={() => setMenuOpen(false)}
                  to="/roster-management"
                >
                  Kokoonpanon hallinta
                </Link>
              </li>
              {isAdmin && (
                <li>
                  <Link onClick={() => setMenuOpen(false)} to="/admin">
                    Admin
                  </Link>
                </li>
              )}
            </>
          )}
        </ul>
      </div>
    </nav>
  );
}
