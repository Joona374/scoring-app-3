import { Link } from "react-router-dom"
import "./Home.css"

export default function Home() {
    return (
        <div>
            <h1>Welcome coach!</h1>
            <Link to="/login" className="home-button">Login</Link>
            <Link to="/register" className="home-button">Register</Link>

        </div>
    )
}