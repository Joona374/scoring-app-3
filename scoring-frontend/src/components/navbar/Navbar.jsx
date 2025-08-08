import "./Navbar.css";
import { useContext, useState } from "react";
import AuthContext from "../../auth/AuthContext";
import { Link, NavLink } from "react-router-dom";

export default function Navbar() {
  const { isLoggedIn, isAdmin } = useContext(AuthContext);
  const [menuOpen, setMenuOpen] = useState(false);

  const toggleMenu = () => setMenuOpen((prev) => !prev);

  return (
    <nav>
      <div className="navbar-left">
        <NavLink
          to="/"
          onClick={() => setMenuOpen(false)}
          style={{ color: "inherit", textDecoration: "none" }}
        >
          ScoringApp 3.0
        </NavLink>
      </div>

      <div className="hamburger" onClick={toggleMenu}>
        ☰
      </div>

      <div className={`navbar-right ${menuOpen ? "open" : ""}`}>
        <ul>
          {!isLoggedIn ? (
            <>
              <li>
                <NavLink
                  onClick={() => setMenuOpen(false)}
                  to="/login"
                  className={({ isActive }) => (isActive ? "active-link" : "")}
                >
                  Kirjaudu
                </NavLink>
              </li>
              <li>
                <NavLink
                  onClick={() => setMenuOpen(false)}
                  to="/register"
                  className={({ isActive }) => (isActive ? "active-link" : "")}
                >
                  Rekisteröidy
                </NavLink>
              </li>
            </>
          ) : (
            <>
              <li>
                <NavLink
                  onClick={() => setMenuOpen(false)}
                  to="/dashboard"
                  className={({ isActive }) => (isActive ? "active-link" : "")}
                >
                  Joukkuesivu
                </NavLink>
              </li>
              <li>
                <NavLink
                  onClick={() => setMenuOpen(false)}
                  to="/tagging"
                  className={({ isActive }) => (isActive ? "active-link" : "")}
                >
                  Tilastointi
                </NavLink>
              </li>
              <li>
                <NavLink
                  onClick={() => setMenuOpen(false)}
                  to="/excel-exporter"
                  className={({ isActive }) => (isActive ? "active-link" : "")}
                >
                  Excel-vienti
                </NavLink>
              </li>
              <li>
                <NavLink
                  onClick={() => setMenuOpen(false)}
                  to="/analysis"
                  className={({ isActive }) => (isActive ? "active-link" : "")}
                >
                  Analyysi
                </NavLink>
              </li>
              <li>
                <NavLink
                  onClick={() => setMenuOpen(false)}
                  to="/roster-management"
                  className={({ isActive }) => (isActive ? "active-link" : "")}
                >
                  Kokoonpanon hallinta
                </NavLink>
              </li>
              {isAdmin && (
                <li>
                  <NavLink
                    onClick={() => setMenuOpen(false)}
                    to="/admin"
                    className={({ isActive }) =>
                      isActive ? "active-link" : ""
                    }
                  >
                    Admin
                  </NavLink>
                </li>
              )}
            </>
          )}
        </ul>
      </div>
    </nav>
  );
}
