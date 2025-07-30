import { useState } from "react";
import "../../components/FormStyles.css";
import "./CreateTeam.css";
import { useNavigate } from "react-router-dom";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function CreateTeam() {
  const [teamName, setTeamName] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [joinCode, setJoinCode] = useState("");
  const [copied, setCopied] = useState(false);

  const reactNavigator = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setErrorMsg("");
    setJoinCode("");
    setCopied(false);

    const token = sessionStorage.getItem("jwt_token");

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
      setJoinCode(data.code_for_team); // store code
      console.log("Set code to:", joinCode);
    } catch (err) {
      setErrorMsg(err.message);
    }
  };

  const copyToClipboard = () => {
    console.log(navigator);
    navigator.clipboard.writeText(joinCode).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="auth-page">
      <h1>Luo joukkue</h1>
      <p className="info-text">
        {" "}
        Olet rekisteröimässä perustajakäyttäjää. <br />
        Luo joukkue ja kutsu muut valmentajat liittymään koodilla.
      </p>
      <form className="auth-form" onSubmit={handleSubmit}>
        <label htmlFor="teamName">Joukkueen nimi</label>
        <input
          id="teamName"
          type="text"
          placeholder="Anna joukkueen nimi"
          value={teamName}
          onChange={(e) => setTeamName(e.target.value)}
          required
        />
        <button type="submit">Luo joukkue</button>
      </form>

      {errorMsg && (
        <p className="error">
          Joukkueen luonti epäonnistui. Oletko jo luonut joukkueen?
        </p>
      )}

      {joinCode && (
        <div className="join-code-container">
          <label htmlFor="joinCode">
            Liittymiskoodi. Jaa tämä joukkueen muille valmentajille.
          </label>
          <div className="join-code-box">
            <input
              id="joinCode"
              type="text"
              value={joinCode}
              readOnly
              onFocus={(e) => e.target.select()}
            />
            <button
              onClick={copyToClipboard}
              className="copy-button"
              type="button"
            >
              Kopioi koodi
            </button>
          </div>
          {copied && <p className="copy-feedback">Kopioitu!</p>}
          <button
            className={"continue-to-teampage-button"}
            onClick={() => reactNavigator("/dashboard")}
          >
            Jatka joukkuesivulle
          </button>
        </div>
      )}
    </div>
  );
}
