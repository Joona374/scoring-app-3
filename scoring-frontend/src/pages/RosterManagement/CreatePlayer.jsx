import { useState } from "react";
import "../../components/FormStyles.css";
import LoadingSpinner from "../../components/LoadingSpinner/LoadingSpinner";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function CreatePlayer({ players, setPlayers }) {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [jerseyNumber, setJerseyNumber] = useState("");

  const [position, setPosition] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);
  const [isLoadingPlayer, setIsLoadingPlayer] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setStatusMessage("");
    setIsLoadingPlayer(true);

    if (position === "") {
      setStatusMessage("Valitse pelipaikka.");
      setIsSuccess(false);
      setIsLoadingPlayer(false);
      return;
    }

    const token = sessionStorage.getItem("jwt_token");

    try {
      const response = await fetch(`${BACKEND_URL}/players/create`, {
        method: "POST",
        headers: {
          "Content-type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          jersey_number: jerseyNumber,
          position,
        }),
      });

      if (!response.ok) {
        const errorBody = await response.json();
        console.error(errorBody);
        setStatusMessage(errorBody.detail || "Pelaajan luominen epäonnistui.");
        setIsSuccess(false);
        setIsLoadingPlayer(false);

        return;
      }

      const data = await response.json();
      console.log(data);
      setStatusMessage("Pelaaja luotu onnistuneesti!");
      setIsSuccess(true);
      const playerObject = {
        id: data.player_id,
        first_name: firstName,
        last_name: lastName,
        position: position,
        jersey_number: jerseyNumber,
      };
      const newPlayers = [...players, playerObject];
      setPlayers(newPlayers);

      setFirstName("");
      setLastName("");
      setJerseyNumber("");
      setPosition("");
      setIsLoadingPlayer(false);
    } catch (err) {
      console.error(err);
      setStatusMessage("Virhe palvelinyhteydessä.");
      setIsSuccess(false);
      setIsLoadingPlayer(false);
    }
  };

  return (
    <div className="auth-page">
      <form className="auth-form" onSubmit={handleSubmit}>
        <div className="form-title">Lisää uusi pelaaja</div>

        <label htmlFor="first-name">Etunimi</label>
        <input
          type="text"
          id="first-name"
          placeholder="Etunimi"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          required
        />

        <label htmlFor="last-name">Sukunimi</label>
        <input
          type="text"
          id="last-name"
          placeholder="Sukunimi"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          required
        />

        <label htmlFor="last-name">Pelinumero</label>
        <input
          type="number"
          id="number"
          placeholder="Pelinumero"
          value={jerseyNumber}
          onChange={(e) => setJerseyNumber(e.target.value)}
          required
          min={0}
          max={99}
        />

        <label htmlFor="position">Pelipaikka</label>
        <select
          id="position"
          value={position}
          onChange={(e) => setPosition(e.target.value)}
          required
        >
          <option value="" disabled>
            -- Valitse pelipaikka --
          </option>
          <option value="Hyökkääjä">Hyökkääjä</option>
          <option value="Puolustaja">Puolustaja</option>
          <option value="Maalivahti">Maalivahti</option>
        </select>

        <button type="submit">
          {" "}
          {isLoadingPlayer ? LoadingSpinner(15) : "Luo Pelaaja"}
        </button>
      </form>

      {statusMessage && (
        <p className={isSuccess ? "success" : "error"}>{statusMessage}</p>
      )}
    </div>
  );
}
