import { Link } from "react-router-dom";
import { useContext, useEffect } from "react";
import AuthContext from "../../auth/AuthContext";
import "./Home.css";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function Home() {
  const { isLoggedIn, logout } = useContext(AuthContext);

  // Wake up backend on page load (Render free tier has cold starts)
  useEffect(() => {
    fetch(`${BACKEND_URL}/`).catch(() => {
      // Silently ignore errors - this is just a wake-up ping
    });
  }, []);

  return (
    <div className="home-hero-container">
      <h1>Seuraa. Analysoi. Voita.</h1>
      <p>
        Moderni valmennustyökalu, joka auttaa muuttamaan datan paremmiksi
        päätöksiksi – helposti ja nopeasti.
      </p>
      <div className="home-hero-buttons">
        {!isLoggedIn ? (
          <>
            <Link to="/register" className="hero-button primary">
              Luo käyttäjä
            </Link>
            <Link to="/login" className="hero-button secondary">
              Kirjaudu sisään
            </Link>
          </>
        ) : (
          <>
            <Link to="/dashboard" className="hero-button primary">
              Siirry joukkuesivulle
            </Link>
            <button onClick={logout} className="hero-button secondary">
              Kirjaudu ulos
            </button>
          </>
        )}
      </div>
    </div>
  );
}
