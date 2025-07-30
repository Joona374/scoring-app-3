import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import AuthContext from "../../auth/AuthContext";
import "../../components/FormStyles.css";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function Login() {
  const [user, setUser] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const navigate = useNavigate();
  const { login, setIsAdmin } = useContext(AuthContext);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setErrorMsg("");
    try {
      const res = await fetch(`${BACKEND_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setErrorMsg(data.detail || "Login failed");
      } else {
        console.log("Login succesful:", data);
        login(data.jwt_token);
        sessionStorage.setItem("username", data.username);
        sessionStorage.setItem("user_id", data.user_id);
        if (data.is_admin) {
          sessionStorage.setItem("is_admin", data.is_admin);
          setIsAdmin(true);
        }
        navigate("/dashboard");
      }
    } catch (err) {
      setErrorMsg("Something went wrong with login");
      console.error("Login error:", err);
    }
  };

  return (
    <div className="auth-page">
      <h1>Kirjaudu sisään</h1>
      <form className="auth-form" onSubmit={handleSubmit}>
        <label htmlFor="user">Käyttäjätunnus tai sähköposti</label>
        <input
          required
          type="text"
          id="user"
          value={user}
          onChange={(e) => setUser(e.target.value)}
        />
        <label htmlFor="password">Salasana</label>
        <input
          required
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Kirjaudu</button>
      </form>
      {errorMsg && <p className="error">{errorMsg}</p>}
    </div>
  );
}
