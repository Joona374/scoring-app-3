import {useState} from "react"
import "./register.css"


export default function Register() {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [confirm, setConfirm] = useState("")

    const handleSubmit = (event) => {
        event.preventDefault();
        console.log(username, password, confirm)
    }

    return (
    <div>
        <h1>Register</h1>
        <form onSubmit={handleSubmit}>
            <label htmlFor="username">Username</label>
            <input type="text" id="username" placeholder="username" value={username} onChange={(e) => setUsername(e.target.value)}  />
            <label htmlFor="password">Password</label>
            <input type="password" id="password" placeholder="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            <label htmlFor="confirm">Confirm Password</label>
            <input type="password" id="confirm" placeholder="confirm password" value={confirm} onChange={(e) => setConfirm(e.target.value)}/>
            <button type="submit">Register</button>
        </form>
    </div>
    )
}