import { useState, useContext } from "react";
import "./Register.css";
import { useNavigate } from "react-router-dom";
import AuthContext from "../../auth/AuthContext";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [code, setCode] = useState("");

  const navigate = useNavigate();
  const { login } = useContext(AuthContext);

  const [errorMsg, setErrorMsg] = useState("");

  const autoLogin = async (creator) => {
    try {
      const res = await fetch(`${BACKEND_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user: username, password: password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setErrorMsg(data.detail || "Login failed");
      } else {
        console.log("Login succesful:", data);
        login(data.jwt_token);
        localStorage.setItem("username", data.username);
        localStorage.setItem("user_id", data.user_id);
        if (creator) {
          navigate("/create-team");
        } else {
          navigate("/dashboard");
        }
      }
    } catch (err) {
      setErrorMsg("Something went wrong with login");
      console.error("Login error:", err);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setErrorMsg("");
    if (password !== confirm) {
      setErrorMsg("Passwords dont match");
      return;
    } else if (password.length < 8) {
      setErrorMsg("Password must be at least 8 characters");
      return;
    } else if (username.includes("@")) {
      setErrorMsg("Username cannot contain '@' ");
    }

    try {
      const res = await fetch(`${BACKEND_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password, code }),
      });

      if (!res.ok) {
        // FastAPI will likely send JSON with detail
        const errBody = await res.json();
        throw new Error(errBody || "Registration failed");
      }

      const data = await res.json();
      console.log("Success:", data);

      const redirect_to_create = data.creator;

      if (redirect_to_create) {
        alert("Registeration succesful! Create your team next.");
      } else {
        alert("Registeration succesful! Redirecting to team dashboard.");
      }

      autoLogin(redirect_to_create);
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message);
    }
  };

  return (
    <div className="register-page">
      <h1>Register</h1>

      <form onSubmit={handleSubmit}>
        <label htmlFor="username">Username</label>
        <input
          required
          type="text"
          id="username"
          placeholder="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <label htmlFor="email">Email</label>
        <input
          required
          type="email"
          id="email"
          placeholder="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <label htmlFor="password">Password</label>
        <input
          required
          type="password"
          id="password"
          placeholder="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <label htmlFor="confirm">Confirm Password</label>
        <input
          required
          type="password"
          id="confirm"
          placeholder="confirm password"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
        />
        <label htmlFor="code">Regiesteration Code</label>
        <input
          type="text"
          id="code"
          placeholder="123ABC"
          minLength="6"
          maxLength="6"
          value={code}
          onChange={(e) => setCode(e.target.value)}
        />
        <button type="submit">Register</button>
      </form>
      {errorMsg && <p className="error">{errorMsg}</p>}
    </div>
  );
}
