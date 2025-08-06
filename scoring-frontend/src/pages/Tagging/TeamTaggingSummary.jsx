import { useContext, useState } from "react";
import "./Styles/TeamTaggingSummary.css";
import { TaggingContext } from "../../context/TaggingContext";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function TeamTaggingSummary() {
  const { taggedEvents, setTaggedEvents } = useContext(TaggingContext);
  const [openIndex, setOpenIndex] = useState(null);

  const toggleOpen = (index) => {
    setOpenIndex((prev) => (prev === index ? null : index));
    console.log(taggedEvents);
  };

  const editTag = async () => {
    console.warn("TODO");
    alert("Ominaisuus työn alla.");
  };

  const deleteTeamTag = async (tag) => {
    const tagId = tag.id;
    const token = sessionStorage.getItem("jwt_token");
    const queryString = `${BACKEND_URL}/tagging/delete/team-tag/${tagId}`;
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
        return;
      }

      const data = await res.json();
      console.log(data);
      const newTags = taggedEvents.filter((tag) => tag.id !== tagId);
      setTaggedEvents(newTags);
    } catch (err) {
      console.error(err);
    }
  };

  const typeDetailFieldMap = {
    "5vs5": "v5v5_type",
    "YV / AV": "pp_type",
    Jatkoaika: "ot_type",
  };

  const tagKeyTranslationMapping = {
    play_result: "Tapahtuma",
    play_type: "Pelitilanne",
    v5v5_type: "5vs5 Tarkenne",
    hahp_papp_type: "HAHP/PAPP Tarkenne",
    hahp_papp_taytto_type: "Täyttö Tarkenne",
    rush_type1: "SHP Tarkenne 1",
    rush_type2: "SHP Tarkenne 2",
    takeaway_type: "Riisto tapahtui",
    takeaway_happ_pahp_type: "Riisto Tarkenne",
    takeaway_kapp_kahp_type: "Riisto Tarkenne",
    takeaway_papp_hahp_type: "Riisto Tarkenne",
    takeaway_jatkopaine_type: "Riisto Tarkenne",
    hahp_papp_alapeli_type: "Alapeli Tarkenne",
    hahp_papp_ylapeli_type: "Yläpeli Tarkenne",
    rebound_type: "Rebound Tarkenne",
    pp_type: "YV Tarkenne",
    pp_blueline_shot_type: "Siniviiva laukaus",
    faceoff_type: "Aloitus Tarkenne",
    v5v5_other_type: "5vs5 Muu Tarkenne",
    pp_faceoff_entry_type: "YV Aloitus/Haku",
    pp_shot_deflection_low_type1: "YV Veto/Ohjaus alhaalta syöttö",
    pp_shot_deflection_low_type2: "YV Veto/Ohjaus alhaalta tarkenne",
    pp_pressure_brokenplay_type: "YV Paine Tarkenne",
    pp_other_type: "YV Muu Tarkenne",
    pp_5vs3_type: "5vs3 Tarkenne",
    pp_av_yv_type: "AV / YV Tarkenne",
    ot_type: "Jatkoaika Tarkenne",
    v3vs3_type: "3vs3 Tarkenne",
    ps_type: "Rangaistuslaukaus Tarkenne",
  };

  return (
    <div className="tagging-summary">
      <h3>Yhteenveto</h3>
      {[...taggedEvents].reverse().map(
        (tag, index) => (
          console.log("Tag:", tag),
          (
            <div
              key={index}
              className={`summary-row ${openIndex === index ? "expanded" : ""}`}
            >
              <div className="summary-header" onClick={() => toggleOpen(index)}>
                <span className="summary-index">
                  {taggedEvents.length - index}.
                </span>
                <span
                  className={
                    tag.play_result === "MP +" || tag.play_result === "Maali +"
                      ? "summary-result summary-result-plus"
                      : "summary-result"
                  }
                >
                  {tag.play_result}
                </span>
                <span className="summary-type">{tag.play_type}</span>
                <span className="summary-type-detail">
                  {tag[typeDetailFieldMap[tag.play_type]]}
                </span>
              </div>

              {openIndex === index && (
                <div className="summary-details">
                  <ul className="tag-details-list">
                    {Object.entries(tag).map(([key, value]) => {
                      if (!value || value === "") return null;
                      if (key === "new_question") return null;
                      if (key === "game_id") return null;
                      if (key === "id") return null;
                      if (key === "timestamp") return null;

                      return (
                        <li key={key}>
                          <strong>
                            {tagKeyTranslationMapping[key] ?? key}:&nbsp;
                          </strong>
                          {value}
                        </li>
                      );
                    })}
                  </ul>
                  <div className="summary-actions">
                    {/* TODO editTag!! */}
                    <button onClick={() => editTag(index)}>Muokkaa</button>
                    <button onClick={() => deleteTeamTag(tag)}>Poista</button>
                  </div>
                </div>
              )}
            </div>
          )
        )
      )}
    </div>
  );
}
