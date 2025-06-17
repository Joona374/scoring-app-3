import { Link } from "react-router-dom"
import "./Home.css"
import { useContext } from "react";
import AuthContext from "../AuthContext";

export default function Home() {
  const { isLoggedIn, logout } = useContext(AuthContext);
  return (
    <div>
      {!isLoggedIn ? (
        <>
          <h1>Welcome coach!</h1>
          <Link to="/login" className="home-button">
            Login
          </Link>
          <Link to="/register" className="home-button">
            Register
          </Link>
        </>
      ) : (
        <>
          <h1>Welcome Back!</h1>
          <button onClick={logout}>Logout</button>
        </>
      )}
    </div>
  );
}