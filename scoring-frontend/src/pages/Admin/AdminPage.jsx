import { useState, useContext } from "react";
import AuthContext from "../../auth/AuthContext";
import "./AdminPage.css";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function AdminPage() {
  const { logout } = useContext(AuthContext);

  const [wipeMessage, setWipeMessage] = useState("");
  const [creatorCode, setCreatorCode] = useState("");
  const [newCodeIdentifier, setNewCodeIdentifier] = useState("");
  const [newCode, setNewCode] = useState("");

  const handleCleanDb = async () => {
    const token = sessionStorage.getItem("jwt_token");
    const res = await fetch(`${BACKEND_URL}/admin/clean-db`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    console.log(res);
    const data = await res.json();
    console.log(data);

    setCreatorCode(data.creator_code);
    setWipeMessage(data.Message);
    console.log(data.creator_code);
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
    </div>
  );
}
