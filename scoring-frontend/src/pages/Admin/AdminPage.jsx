import { useState, useContext, useEffect } from "react";
import AuthContext from "../../auth/AuthContext";
import "./AdminPage.css";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function AdminPage() {
  const { logout } = useContext(AuthContext);

  const [wipeMessage, setWipeMessage] = useState("");
  const [creatorCode, setCreatorCode] = useState("");
  const [newCodeIdentifier, setNewCodeIdentifier] = useState("");
  const [newCode, setNewCode] = useState("");
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState("");
  const [teamChangeMessage, setTeamChangeMessage] = useState("");

  useEffect(() => {
    async function fetchData() {
      // your async code here
      setTeams(await fetchTeams());
    }
    fetchData();
  }, []);

  const changeAdminTeam = async (teamId) => {
    const token = sessionStorage.getItem("jwt_token");
    const res = await fetch(
      `${BACKEND_URL}/admin/change-admin-team?new_team_id=${teamId}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      }
    );
    const data = await res.json();
    console.log(data);
    setTeamChangeMessage(data.Message);
    return data;
  };

  const fetchTeams = async () => {
    const token = sessionStorage.getItem("jwt_token");
    const res = await fetch(`${BACKEND_URL}/admin/teams`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await res.json();
    return data.teams;
  };

  const handleCleanDb = async () => {
    const token = sessionStorage.getItem("jwt_token");
    const res = await fetch(`${BACKEND_URL}/admin/clean-db`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await res.json();

    setCreatorCode(data.creator_code);
    setWipeMessage(data.Message);
    logout();
  };

  const createNewCode = async (event) => {
    event.preventDefault();
    const token = sessionStorage.getItem("jwt_token");
    const res = await fetch(`${BACKEND_URL}/admin/create-code`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ new_code_identifier: newCodeIdentifier }),
    });

    if (!res.ok) {
      console.error("Error creating a new code");
    }

    const data = await res.json();
    setNewCode(data.code);
  };

  return (
    <div className="admin-wrapper">
      <div className="reset-db-wrapper auth-form">
        <button onClick={handleCleanDb}>Reset DB</button>
        <p>{wipeMessage}</p>
        <p>{creatorCode}</p>
      </div>
      <div className="create-code-wrapper">
        <form className="auth-form" onSubmit={createNewCode}>
          <label htmlFor="identifier">Identifier</label>
          <input
            type="text"
            id="identifier"
            placeholder="Identifier"
            value={newCodeIdentifier}
            onChange={(e) => setNewCodeIdentifier(e.target.value)}
            required
          />

          <label htmlFor="new-reg-code">New Creator Code</label>
          <input
            type="text"
            id="new-reg-code"
            placeholder=""
            value={newCode}
            readOnly
          />

          {newCode && <p className="success">Uusi koodi lisätty</p>}

          <button type="submit">Create New Code</button>
        </form>
      </div>

      <div className="change-team-wrapper">
        <div className="auth-form">
          <label htmlFor="teams">Select Team</label>
          <select
            id="teams"
            value={selectedTeam}
            onChange={(e) => setSelectedTeam(e.target.value)}
          >
            <option value="">-- Select a team --</option>
            {teams.map((team) => (
              <option key={team.id} value={team.id}>
                {team.name}
              </option>
            ))}
          </select>
          {/* Some kind of button to perform an action with the selected team */}
          <button
            disabled={!selectedTeam}
            onClick={() => changeAdminTeam(selectedTeam)}
          >
            Select users team
          </button>
          <p className="team-change-message">{teamChangeMessage}</p>
        </div>
      </div>
    </div>
  );
}
