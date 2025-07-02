import { useEffect, useState } from "react";
import "./Dashboard.css";

export default function TeamDashboard() {
  const [teamname, setTeamname] = useState("");
  const [joinCode, setJoinCode] = useState("");
  const [players, setPlayers] = useState([]);

  useEffect(() => {
    const fetchTeamInfo = async () => {
      const token = sessionStorage.getItem("jwt_token");
      const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

      try {
        const response = await fetch(`${BACKEND_URL}/teams/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch user info");
        }

        const data = await response.json();
        setTeamname(data.team_name);
        setJoinCode(data.join_code);
        setPlayers(data.players);

        console.log(data);
      } catch (err) {
        console.log("Error:", err);
        setTeamname("Error loading username");
      }
    };

    fetchTeamInfo();
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      {teamname ? (
        <>
          <h3>Welcome {teamname}</h3>
          <h4>Join code: {joinCode}</h4>
          <ul className="dashboard-players">
            {players.map((player, index) => {
              return (
                <li key={index}>
                  {index + 1} {player.first_name} {player.last_name}{" "}
                  {player.position}{" "}
                </li>
              );
            })}
          </ul>
        </>
      ) : (
        <h3>Loading...</h3>
      )}
    </div>
  );
}
