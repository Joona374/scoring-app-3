import { Link } from "react-router-dom";
import { useContext } from "react";
import AuthContext from "../../auth/AuthContext";
import "./Home.css";

export default function Home() {
  const { isLoggedIn, logout } = useContext(AuthContext);

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
