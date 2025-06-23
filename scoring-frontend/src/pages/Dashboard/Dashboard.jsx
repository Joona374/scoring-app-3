import { Link } from "react-router-dom";

export default function Dashboard() {
  const username = "User";

  return (
    <div>
      <h1>Dashboard</h1>
      <h3>Welcome {username}</h3>
      <Link to="/">Home</Link>
    </div>
  );
}
