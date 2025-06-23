import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function Dashboard() {
  const [username, setUsername] = useState("Loading...");

  useEffect(() => {
    const fetchUserinfo = async () => {
      const token = localStorage.getItem("jwt_token");
      const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

      try {
        const response = await fetch(`${BACKEND_URL}/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch user info");
        }

        const data = await response.json();
        setUsername(data.username);
      } catch (err) {
        console.log("Error:", err);
        setUsername("Error loading username");
      }
    };

    fetchUserinfo();
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      <h3>Welcome {username}</h3>
      <Link to="/">Home</Link>
    </div>
  );
}
