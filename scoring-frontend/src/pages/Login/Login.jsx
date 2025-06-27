import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import AuthContext from "../../auth/AuthContext";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function Login() {
  const [user, setUser] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);

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
        localStorage.setItem("username", data.username);
        localStorage.setItem("user_id", data.user_id);
        navigate("/dashboard");
      }
    } catch (err) {
      setErrorMsg("Something went wrong with login");
      console.error("Login error:", err);
    }
  };

  return (
    <div>
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="user">Username of Email</label>
        <input
          required
          type="text"
          placeholder="User"
          id="user"
          value={user}
          onChange={(e) => setUser(e.target.value)}
        />
        <label htmlFor="password">Password</label>
        <input
          required
          type="password"
          placeholder="Password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Login</button>
      </form>
      {errorMsg && <p>{errorMsg}</p>}
    </div>
  );
}
