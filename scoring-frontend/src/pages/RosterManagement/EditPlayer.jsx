import { useEffect, useState } from "react";
import "../../components/FormStyles.css";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function UpdatePlayer({ players, setPlayers, player }) {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [number, setNumber] = useState(null);
  const [position, setPosition] = useState("");
  const [playerId, setPlayerId] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);

  const positionMapping = {
    FORWARD: "Hyökkääjä",
    DEFENDER: "Puolustaja",
    GOALIE: "Maalivahti",
  };

  useEffect(() => {
    setFirstName(player.first_name);
    setLastName(player.last_name);
    setNumber(player.jersey_number);
    if (["FORWARD", "DEFENDER", "GOALIE"].includes(player.position)) {
      setPosition(positionMapping[player.position]);
    } else setPosition(player.position);

    setPlayerId(player.id);
  }, [player]);

  const handleDelete = async (event) => {
    event.preventDefault();
    setStatusMessage("");

    const confirmed = window.confirm(
      `Haluatko varmasti poistaa pelaajan ${firstName} ${lastName}? Pelaajan tilastot poistetaan pysyvästi.`
    );
    if (!confirmed) return;

    const token = sessionStorage.getItem("jwt_token");

    try {
      if (!playerId) {
        console.error("No player ID selected");
        setStatusMessage("Virhe pelaajan ID:n lukemisessa.");
        setIsSuccess(false);
      }

      const response = await fetch(
        `${BACKEND_URL}/players/delete/${playerId}`,
        {
          method: "DELETE",
          headers: {
            "Content-type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        const errorBody = await response.json();
        console.error(errorBody);
        setStatusMessage(
          errorBody.detail || "Pelaajan poistaminen epäonnistui."
        );
        setIsSuccess(false);
        return;
      }

      const data = await response.json();
      console.log(data);
      setStatusMessage("Pelaaja poistettu onnistuneesti.");
      setIsSuccess(true);

      const newPlayers = players.filter((player) => player.id !== playerId);
      setPlayers(newPlayers);
    } catch (err) {
      console.error(err);
      setStatusMessage("Virhe palvelinyhteydessä.");
      setIsSuccess(false);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setStatusMessage("");

    const playerBody = {};
    if (firstName) {
      playerBody.first_name = firstName;
    }
    if (lastName) {
      playerBody.last_name = lastName;
    }
    if (number) {
      player.jersey_number = number;
    }
    if (position) {
      playerBody.position = position;
    }

    const token = sessionStorage.getItem("jwt_token");

    try {
      if (!playerId) {
        console.error("No player ID selected");
        setStatusMessage("Virhe pelaajan ID:n lukemisessa.");
        setIsSuccess(false);
      }

      const response = await fetch(
        `${BACKEND_URL}/players/update/${playerId}`,
        {
          method: "PATCH",
          headers: {
            "Content-type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(playerBody),
        }
      );

      if (!response.ok) {
        const errorBody = await response.json();
        console.error(errorBody);
        setStatusMessage(
          errorBody.detail || "Pelaajan päivittäminen epäonnistui."
        );
        setIsSuccess(false);
        return;
      }

      const data = await response.json();
      console.log(data);
      setStatusMessage("Pelaaja päivitetty onnistuneesti!");
      setIsSuccess(true);
      const updatedPlayer = {
        id: data.id,
        first_name: firstName,
        last_name: lastName,
        jersey_number: number,
        position: position,
      };
      console.log("UPDATED:", updatedPlayer);
      const newPlayers = players.map((player) => {
        if (player.id === updatedPlayer.id) return updatedPlayer;
        else return player;
      });
      setPlayers(newPlayers);
    } catch (err) {
      console.error(err);
      setStatusMessage("Virhe palvelinyhteydessä.");
      setIsSuccess(false);
    }
  };

  return (
    <div className="auth-page">
      <form className="auth-form">
        <div className="form-title">Muokkaa pelaajaa</div>

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

        <label htmlFor="number">Pelinumero</label>
        <input
          type="number"
          min={0}
          max={99}
          id="number"
          placeholder="Pelinumero"
          value={number}
          onChange={(e) => setNumber(e.target.value)}
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

        <div className="action-buttons">
          <button
            className="auth-form button"
            id="save-btn"
            onClick={handleSubmit}
          >
            Tallenna
          </button>
          <button
            className="auth-form button delete-button"
            id="delete-btn"
            onClick={handleDelete}
          >
            Poista
          </button>
        </div>
      </form>

      {statusMessage && (
        <p className={isSuccess ? "success" : "error"}>{statusMessage}</p>
      )}
    </div>
  );
}
