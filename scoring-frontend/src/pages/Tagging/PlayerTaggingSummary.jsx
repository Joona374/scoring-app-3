import { useContext, useState } from "react";
import "./Styles/PlayerTaggingSummary.css";
import { TaggingContext } from "../../context/TaggingContext";
import LoadingSpinner from "../../components/LoadingSpinner/LoadingSpinner";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function PlayerTaggingSummary() {
  const { taggedEvents, setTaggedEvents } = useContext(TaggingContext);
  const [openIndex, setOpenIndex] = useState(null);
  const [isLoadingDeleteTag, setIsLoadingDeleteTag] = useState(false);

  const toggleOpen = (index) => {
    setOpenIndex((prev) => (prev === index ? null : index));
  };

  const editTag = async () => {
    console.warn("TODO");
    alert("Ominaisuus työn alla.");
  };

  const deletePlayerTag = async (tag) => {
    setIsLoadingDeleteTag(true);
    const tagId = tag.id;
    const token = sessionStorage.getItem("jwt_token");
    const queryString = `${BACKEND_URL}/tagging/delete/player-tag/${tagId}`;
    try {
      const res = await fetch(queryString, {
        method: "DELETE",
        headers: {
          "Content-type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        console.log("Issue deleting tag");
        alert("Tapahtui virhe poistaessa maalipaikkaa.");
        setIsLoadingDeleteTag(false);
        return;
      }

      const data = await res.json();
      const newTags = taggedEvents.filter((tag) => tag.id !== tagId);
      setTaggedEvents(newTags);
      setIsLoadingDeleteTag(false);
    } catch (err) {
      console.error(err);
      alert("Tapahtui virhe poistaessa maalipaikkaa.");
      setIsLoadingDeleteTag(false);
    }
  };

  const summaryKeyMapping = {
    shotZone: "Laukauksen alue",
    netZone: "Maalin alue",
    shot_result: "Laukauksen tulos",
    shot_type: "Laukauksen tyyppi",
    strengths: "Pelitilanne",
    crossice: "Keskilinjan ylittävä",
  };

  const shotZoneMapping = {
    ZONE_1: "1. Alue ",
    ZONE_2_MIDDLE: "2. Alue keskeltä",
    ZONE_2_SIDE: "2. Alue sivusta",
    HIGH_SLOT: "Ringetteviiva",
    BLUELINE: "Siniviiva",
    ZONE_4: "4. Alue",
    OUTSIDE_FAR: "Pienikulma (Kaukana)",
    OUTSIDE_CLOSE: "Pienikulma (Lähellä)",
    MISC: "Muut",
  };

  const netZoneMapping = {
    "Mid-Mid": "Keskelle",
    "Mid-Left": "Puolikorkea vasen",
    "Mid-Right": "Puolikorkea oikea",
    "Low-Left": "Matala vasen",
    "Low-Right": "Matala oikea",
    "Top-Left": "Korkea vasen",
    "Top-Right": "Korkea oikea",
    "Top-Mid": "Korkea keskellä",
    "Low-Mid": "Matala keskellä",
  };

  const strengthsMappings = {
    ES: "Tasakentällisin",
    PP: "Ylivoimalla",
    PK: "Alivoimalla",
    "EN+": "6 vs 5",
    "EN-": "5 vs 6",
  };

  return (
    <div className="player-tagging-summary">
      <h3>Yhteenveto</h3>
      {[...taggedEvents].reverse().map((tag, index) => (
        <div
          key={index}
          className={`player-summary-row ${
            openIndex === index ? "expanded" : ""
          }`}
        >
          <div
            className="player-summary-header"
            onClick={() => toggleOpen(index)}
          >
            <span className="player-summary-index">
              {taggedEvents.length - index}.
            </span>
            <span
              className={
                tag.shot_result === "MP +" ||
                tag.shot_result === "Maali +" ||
                tag.shot_result === "Laukaus +"
                  ? "player-summary-result player-summary-result-plus"
                  : "player-summary-result"
              }
            >
              {tag.shot_result}
            </span>
            <span className="player-summary-type">{tag.shot_type}</span>
            {tag.shooter && (
              <span className="player-summary-shooter">
                {tag.shooter.last_name} {tag.shooter.first_name.slice(0, 1)}.
              </span>
            )}
          </div>

          {openIndex === index && (
            <div className="player-summary-details">
              <ul className="tag-details-list">
                {Object.entries(tag).map(([key, value]) => {
                  console.log("Key:", key, "Value:", value);
                  if (value === null || value === "") {
                    console.log("Skipping empty value for key:", key);
                    return null;
                  }
                  if (key === "new_question") return null;
                  if (key === "game_id") return null;
                  if (key === "location") return null;
                  if (key === "net") return null;
                  if (key === "on_ices") return null;
                  if (key === "participations") return null;
                  if (key === "id") return null;

                  if (key === "shooter") {
                    return (
                      <li key={key}>
                        <strong>Laukoja:&nbsp;</strong>
                        {value.last_name} {value.first_name}
                      </li>
                    );
                  }

                  if (key === "shotZone") {
                    return (
                      <li key={key}>
                        <strong>{summaryKeyMapping[key]}:&nbsp;</strong>
                        {shotZoneMapping[value] || value}
                      </li>
                    );
                  }

                  if (key === "crossice") {
                    return (
                      <li key={key}>
                        <strong>{summaryKeyMapping[key]}:&nbsp;</strong>
                        {value ? "Kyllä" : "Ei"}
                      </li>
                    );
                  }

                  if (key === "netZone") {
                    return (
                      <li key={key}>
                        <strong>{summaryKeyMapping[key]}:&nbsp;</strong>
                        {netZoneMapping[value] || value}
                      </li>
                    );
                  }

                  if (key === "strengths") {
                    return (
                      <li key={key}>
                        <strong>{summaryKeyMapping[key]}:&nbsp;</strong>
                        {strengthsMappings[value] || value}
                      </li>
                    );
                  }

                  return (
                    <li key={key}>
                      <strong>{summaryKeyMapping[key]}:&nbsp;</strong>
                      {value}
                    </li>
                  );
                })}
              </ul>
              <div className="summary-actions">
                {/* TODO editTag!! */}
                <button onClick={() => editTag(index)}>Muokkaa</button>
                <button
                  onClick={() => deletePlayerTag(tag)}
                  disabled={isLoadingDeleteTag}
                >
                  {isLoadingDeleteTag ? LoadingSpinner(18) : "Poista"}
                </button>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
