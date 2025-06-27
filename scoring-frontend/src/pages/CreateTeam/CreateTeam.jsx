import { useState } from "react";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function CreateTeam() {
  const [teamName, setTeamName] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const handleSubmit = async (event) => {
    setErrorMsg("");
    event.preventDefault();
    console.log("Submit");
    console.log(teamName);

    const token = localStorage.getItem("jwt_token");

    try {
      const response = await fetch(`${BACKEND_URL}/teams/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name: teamName }),
      });

      if (!response.ok) {
        const errorBody = await response.json();
        setErrorMsg(errorBody || "Team creation failed");
        return;
      }

      const data = await response.json();
      console.log(data);
      setErrorMsg(`Team JOIN code: ${data.code_for_team}`);
    } catch (err) {
      setErrorMsg(err.message);
    }
  };

  return (
    <div className="create-team-page">
      <h1>Create Team</h1>
      <form onSubmit={handleSubmit}>
        <input
          required
          type="text"
          value={teamName}
          onChange={(e) => setTeamName(e.target.value)}
        />
        <button>Send</button>
      </form>
      {errorMsg && <p className="error">{errorMsg}</p>}
    </div>
  );
}
