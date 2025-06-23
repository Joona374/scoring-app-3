import { Link } from "react-router-dom";
import "./Home.css";
import { useContext } from "react";
import AuthContext from "../../auth/AuthContext";

export default function Home() {
  const { isLoggedIn, logout } = useContext(AuthContext);
  return (
    <div>
      {!isLoggedIn ? (
        <>
          <h1>Welcome coach!</h1>
          <div className="home-buttons">
            <Link to="/login" className="home-button">
              Login
            </Link>
            <Link to="/register" className="home-button">
              Register
            </Link>
          </div>
        </>
      ) : (
        <>
          <h1>Welcome Back!</h1>
          <Link to="/dashboard" className="home-button">
            Dashboard
          </Link>
          <button onClick={logout} className="home-button">
            Logout
          </button>
        </>
      )}
    </div>
  );
}
