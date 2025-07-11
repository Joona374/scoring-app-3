import { useState } from "react";
import "../../components/FormStyles.css";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function CreatePlayer() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [position, setPosition] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setStatusMessage("");

    if (position === "") {
      setStatusMessage("Valitse pelipaikka.");
      setIsSuccess(false);
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
          position,
        }),
      });

      if (!response.ok) {
        const errorBody = await response.json();
        console.error(errorBody);
        setStatusMessage(errorBody.detail || "Pelaajan luominen epäonnistui.");
        setIsSuccess(false);
        return;
      }

      const data = await response.json();
      console.log(data);
      setStatusMessage("Pelaaja luotu onnistuneesti!");
      setIsSuccess(true);
      setFirstName("");
      setLastName("");
      setPosition("");
    } catch (err) {
      console.error(err);
      setStatusMessage("Virhe palvelinyhteydessä.");
      setIsSuccess(false);
    }
  };

  return (
    <div className="auth-page">
      <h1>Luo pelaaja</h1>
      <form className="auth-form" onSubmit={handleSubmit}>
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

        <button type="submit">Luo pelaaja</button>
      </form>

      {statusMessage && (
        <p className={isSuccess ? "success" : "error"}>{statusMessage}</p>
      )}
    </div>
  );
}
