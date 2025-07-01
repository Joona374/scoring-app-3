import { useState } from "react";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function CreatePlayer() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [position, setPosition] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    console.log("Create player");
    console.log(firstName, lastName, position);
    if (position === "") return;

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
        console.log("Error creating player");
        console.error(errorBody);
      }

      const data = await response.json();
      console.log(data);
      alert("Player created successfully");
    } catch (err) {
      console.log("Error creating player");
      console.log(err);
      return;
    }
  };

  return (
    <div>
      <h1>Create Player</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="first-name">First Name</label>
        <input
          type="text"
          id="first-name"
          placeholder="First name"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
        />
        <label htmlFor="last-name">Last Name</label>
        <input
          type="text"
          id="last-name"
          placeholder="Last name"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
        />
        <label htmlFor="position">Position</label>
        <select
          name="position"
          id="position"
          value={position}
          onChange={(e) => setPosition(e.target.value)}
        >
          <option value="" disabled>
            -- Valitse pelipaikka --
          </option>
          <option value="Hyökkääjä">Hyökkääjä</option>
          <option value="Puolustaja">Puolustaja</option>
          <option value="Maalivahti">Maalivahti</option>
        </select>
        <button>Create Player</button>
      </form>
    </div>
  );
}
