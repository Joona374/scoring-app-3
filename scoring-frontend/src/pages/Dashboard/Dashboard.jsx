import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";
import LoadingSpinner from "../../components/LoadingSpinner/LoadingSpinner";
import LinkButton from "../../components/LinkButton/LinkButton";

export default function TeamDashboard() {
  const [teamname, setTeamname] = useState("");
  const [joinCode, setJoinCode] = useState("");
  const [players, setPlayers] = useState([]);
  const navigator = useNavigate();

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
        if (
          data.team_name === null &&
          data.players === null &&
          data.join_code === null
        ) {
          setTeamname("Sinulla ei ole vielä joukkuetta.");
          navigator("/create-team");
        }
        console.log(data);
      } catch (err) {
        console.log("Error:", err);
        setTeamname("Virhe joukkueen haussa.");
      }
    };

    fetchTeamInfo();
  }, []);

  return (
    <div className="dashboard-wrapper">
      {teamname ? (
        <>
          <h1 style={{ marginBottom: "1rem", fontSize: "3rem" }}>{teamname}</h1>
          <h4 style={{ marginBottom: "1rem", fontSize: "1.2rem" }}>
            Liittymiskoodi: {joinCode}
          </h4>
          {/* <ul className="dashboard-players">
            {players.map((player, index) => {
              return (
                <li key={index}>
                  {index + 1} {player.first_name} {player.last_name}{" "}
                  {player.position}{" "}
                </li>
              );
            })}
          </ul> */}
        </>
      ) : (
        LoadingSpinner(25)
      )}
      {/* <LinkButton
        text="Kokoonpanon hallinta"
        path="/roster-management"
      ></LinkButton> */}
      <div className="coming-soon-wrapper">
        <h1 style={{ fontSize: "3rem" }} className="coming-soon-h1">
          Joukkuesivu tulossa pian!
        </h1>
      </div>
    </div>
  );
}
