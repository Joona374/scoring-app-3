import { useState } from "react";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function AdminPage() {
  const [wipeMessage, setWipeMessage] = useState("");
  const [creatorCode, setCreatorCode] = useState("");

  const handleClick = async () => {
    const res = await fetch(`${BACKEND_URL}/admin/clean-db`, {
      method: "POST",
    });
    console.log(res);
    const data = await res.json();
    console.log(data);

    setCreatorCode(data.creator_code);
    setWipeMessage(data.Message);
    console.log(data.creator_code);
  };

  return (
    <>
      <button onClick={handleClick}>Reset DB</button>
      <p>{wipeMessage}</p>
      <p>{creatorCode}</p>
    </>
  );
}
