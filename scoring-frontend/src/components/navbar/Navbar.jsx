import "./Navbar.css";
import { useContext } from "react";
import AuthContext from "../../auth/AuthContext";

export default function Navbar() {
  const { isLoggedIn } = useContext(AuthContext);

  return (
    <nav>
      <ul>
        <li>
          <a href="/">Home</a>
        </li>
        {!isLoggedIn ? (
          <>
            {" "}
            <li>
              <a href="/register">Register</a>
            </li>
            <li>
              <a href="/login">Login</a>
            </li>
          </>
        ) : (
          <li>
            <a href="/dashboard">Dashboard</a>
          </li>
        )}
      </ul>
    </nav>
  );
}
