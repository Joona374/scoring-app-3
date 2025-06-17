import {useState} from "react"
import "./Register.css"
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function Register() {
    const [username, setUsername] = useState("")
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [confirm, setConfirm] = useState("")

    const [errorMsg, setErrorMsg] = useState("");

    const handleSubmit = async (event) => {
        event.preventDefault();
        setErrorMsg("");
        if (password !== confirm) {
          setErrorMsg("Passwords dont match")
          return;
        }
        else if (password.length < 8) {
          setErrorMsg("Password must be at least 8 characters");
          return
        }

        else if (username.includes("@")) {
          setErrorMsg("Username cannot contain '@'")
        }
        
        try {
          const res = await fetch(`${BACKEND_URL}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password })
        });

          if (!res.ok) {
            // FastAPI will likely send JSON with detail
            const errBody = await res.json();
            throw new Error(errBody || "Registration failed");
          }

          const data = await res.json();
          console.log("Success:", data);
          // TODO: redirect to /login or auto‑login

        } catch (err) {
          console.error(err);
          setErrorMsg(err.message);
    }


    }

    return (
    <div className="register-page">
      <h1>Register</h1>

      <form onSubmit={handleSubmit}>
        <label htmlFor="username">Username</label>
        <input required type="text" id="username" placeholder="username" value={username} onChange={(e) => setUsername(e.target.value)}  />
        <label htmlFor="email">Email</label>
        <input required type="email" id="email" placeholder="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <label htmlFor="password">Password</label>
        <input required type="password" id="password" placeholder="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <label htmlFor="confirm">Confirm Password</label>
        <input required type="password" id="confirm" placeholder="confirm password" value={confirm} onChange={(e) => setConfirm(e.target.value)}/>
        <button type="submit">Register</button>
      </form>
      {errorMsg && <p className="error">{errorMsg}</p>}
    </div>
    )
}