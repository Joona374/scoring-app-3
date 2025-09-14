import { useEffect, useState } from "react";
import "./RosterSelector.css";
import RosterBox from "./RosterBox";
import LoadingSpinner from "../LoadingSpinner/LoadingSpinner";
import BasicButton from "../../components/BasicButton/BasicButton";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function RosterSelector({
  setShowRosterSelector,
  playersInTeam,
  playersInRoster,
  updateRoster,
}) {
  const [selectingPosition, setSelectingPosition] = useState("");
  const [scraperUrl, setScraperUrl] = useState("");
  const [scraperLocation, setScraperLocation] = useState("koti");
  const [isLoadingScrapedRoster, setIsLoadingScrapedRoster] = useState(false);
  const [draftRoster, setDraftRoster] = useState([]);

  useEffect(() => {
    setDraftRoster([...playersInRoster]);
  }, []);

  const handlePlayerListClick = (target, index) => {
    if (selectingPosition) {
      const player = playersInTeam[index];

      const [line, position] = selectingPosition.split("-");
      const rosterSpotIndex = draftRoster.findIndex(
        (spot) => spot.line === parseInt(line) && spot.position === position
      );
      let newPlayersInRoster = draftRoster.map((spot, index) => {
        if (index === rosterSpotIndex) {
          return { ...spot, player: player };
        }
        return spot;
      });
      setDraftRoster(newPlayersInRoster);

      if (rosterSpotIndex < 24) {
        const nextSpot = draftRoster[rosterSpotIndex + 1];
        setSelectingPosition(`${nextSpot.line}-${nextSpot.position}`);
      }
    } else {
      alert("Valitse pelipaikka ennen pelaajan valintaa");
    }
  };

  const removePlayerFromRosterSpot = (rosterSpot) => {
    const parts = rosterSpot.split("-");
    const line = parseInt(parts[0]);
    const position = parts[1];
    const newPlayersInRoster = draftRoster.map((rosterSpot, idx) => {
      if (rosterSpot.line === line && rosterSpot.position === position) {
        const editedRosterSpot = { ...rosterSpot, player: null };
        return editedRosterSpot;
      }
      return rosterSpot;
    });
    setDraftRoster(newPlayersInRoster);
  };

  const handleScraperSubmit = async (e) => {
    setIsLoadingScrapedRoster(true);
    e.preventDefault();
    if (!scraperUrl) {
      setIsLoadingScrapedRoster(false);
      return;
    }
    const token = sessionStorage.getItem("jwt_token");

    try {
      const response = await fetch(
        `${BACKEND_URL}/games/scrape-roster?game_url=${encodeURIComponent(
          scraperUrl
        )}&home=${scraperLocation === "koti" ? "home" : "away"}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (!response.ok) {
        setIsLoadingScrapedRoster(false);
        throw new Error("Network response was not ok");
      }
      const data = await response.json();
      fillRoster(data);
      setIsLoadingScrapedRoster(false);
    } catch (error) {
      setIsLoadingScrapedRoster(false);
      console.error("Error fetching roster:", error);
      alert("Kokoonpanon haku epäonnistui. Tarkista URL ja yritä uudelleen.");
    }
  };

  const fillRoster = (scrapedRoster) => {
    let newPlayersInRoster = Object.entries(scrapedRoster).map(
      ([pos, player]) => {
        const [line, position] = pos.split("-");
        const matchedPlayer = playersInTeam.find((p) => p.id === player.id);
        return {
          line: parseInt(line),
          position: position,
          player: matchedPlayer || null,
        };
      }
    );

    setDraftRoster(newPlayersInRoster);
  };

  const confirmRoster = () => {
    updateRoster(draftRoster);
    setShowRosterSelector(false);
  };

  const rostersAreEqual = () => {
    for (let i = 0; i < draftRoster.length; i++) {
      const draftRosterSpot = draftRoster[i];
      const currentRosterSpot = playersInRoster[i];

      if (
        draftRosterSpot.player === null ||
        currentRosterSpot.player === null
      ) {
        if (
          draftRosterSpot.player === null &&
          currentRosterSpot.player === null
        ) {
          continue;
        }
        return false;
      } else if (draftRosterSpot.player.id !== currentRosterSpot.player.id)
        return false;
    }
    return true;
  };

  const cancelRoster = () => {
    if (!rostersAreEqual()) {
      const confirmation = confirm(
        "Oletko varma että haluat perua muutokset kokoonpaanon?"
      );
      if (!confirmation) return;
    }
    setShowRosterSelector(false);
  };

  return (
    <div className="roster-selector-wrapper">
      <div className="roster-selector">
        <div className="lineup">
          <div className="skaters">
            <div className="left-roster-column">
              {["1", "2", "3", "4"].map((num) => {
                return (
                  <div className="positions-row" key={`${num}-DROW`}>
                    {[`${num}-LD`, `${num}-RD`].map((position_id) => {
                      const rosterSpot = draftRoster.find(
                        (spot) =>
                          `${spot.line}-${spot.position}` === position_id
                      );

                      const playerForThisBox = rosterSpot
                        ? rosterSpot.player
                        : null;
                      return (
                        <RosterBox
                          id={position_id}
                          key={position_id}
                          player={playerForThisBox}
                          selectingPosition={selectingPosition}
                          setSelectingPosition={setSelectingPosition}
                          removePlayerFromRosterspot={
                            removePlayerFromRosterSpot
                          }
                        />
                      );
                    })}
                  </div>
                );
              })}
            </div>
            <div className="right-roster-column">
              {["1", "2", "3", "4", "5"].map((num) => {
                return (
                  <div className="positions-row" key={`${num}-FROW`}>
                    {[`${num}-LW`, `${num}-C`, `${num}-RW`].map(
                      (position_id) => {
                        const rosterSpot = draftRoster.find(
                          (spot) =>
                            `${spot.line}-${spot.position}` === position_id
                        );
                        const playerForThisBox = rosterSpot
                          ? rosterSpot.player
                          : null;

                        return (
                          <RosterBox
                            id={position_id}
                            key={position_id}
                            player={playerForThisBox}
                            selectingPosition={selectingPosition}
                            setSelectingPosition={setSelectingPosition}
                            removePlayerFromRosterspot={
                              removePlayerFromRosterSpot
                            }
                          />
                        );
                      }
                    )}
                  </div>
                );
              })}
            </div>
          </div>
          <div className="goalies-row">
            {["1-G", "2-G"].map((position_id) => {
              const rosterSpot = draftRoster.find(
                (spot) => `${spot.line}-${spot.position}` === position_id
              );
              const playerForThisBox = rosterSpot ? rosterSpot.player : null;
              return (
                <RosterBox
                  id={position_id}
                  key={position_id}
                  player={playerForThisBox}
                  selectingPosition={selectingPosition}
                  setSelectingPosition={setSelectingPosition}
                  removePlayerFromRosterspot={removePlayerFromRosterSpot}
                />
              );
            })}
          </div>
          <div className="roster-controls">
            <BasicButton text="Vahvista" onClickMethod={confirmRoster} />
            <BasicButton text="Peruuta" onClickMethod={cancelRoster} />

            <form
              onSubmit={handleScraperSubmit}
              className="scraper-roster-input"
            >
              <input
                type="text"
                placeholder="Kopioi tähän linkki tulospalvelun ottelusivulle"
                value={scraperUrl}
                onChange={(e) => setScraperUrl(e.target.value)}
              />
              <input
                type="radio"
                value="koti"
                checked={scraperLocation === "koti"}
                onChange={(e) => setScraperLocation(e.target.value)}
              />{" "}
              Koti
              <input
                type="radio"
                value="vieras"
                checked={scraperLocation === "vieras"}
                onChange={(e) => setScraperLocation(e.target.value)}
              />{" "}
              Vieras
              <button disabled={!scraperUrl} type="submit">
                {isLoadingScrapedRoster ? LoadingSpinner(18) : "Hae kokoonpano"}
              </button>
            </form>
          </div>
        </div>
        <div className="player-list">
          <details open>
            <summary>Hyökkääjät</summary>
            {playersInTeam
              .filter((p) => p.position === "FORWARD")
              .sort((a, b) => a.last_name.localeCompare(b.last_name))
              .map((player, index) => (
                <p
                  key={`F-${index}`}
                  onClick={(event) =>
                    handlePlayerListClick(
                      event.target,
                      playersInTeam.indexOf(player)
                    )
                  }
                >
                  <span className="player-jersey-number">
                    #{player.jersey_number}{" "}
                  </span>
                  <span>
                    {" "}
                    {player.last_name} {player.first_name}
                  </span>
                </p>
              ))}
          </details>

          <details open>
            <summary>Puolustajat</summary>
            {playersInTeam
              .filter((p) => p.position === "DEFENDER")
              .sort((a, b) => a.last_name.localeCompare(b.last_name))
              .map((player, index) => (
                <p
                  key={`D-${index}`}
                  onClick={(event) =>
                    handlePlayerListClick(
                      event.target,
                      playersInTeam.indexOf(player)
                    )
                  }
                >
                  <span className="player-jersey-number">
                    #{player.jersey_number}{" "}
                  </span>
                  <span>
                    {player.last_name} {player.first_name}
                  </span>
                </p>
              ))}
          </details>

          <details open>
            <summary>Maalivahdit</summary>
            {playersInTeam
              .filter((p) => p.position === "GOALIE")
              .sort((a, b) => a.last_name.localeCompare(b.last_name))
              .map((player, index) => (
                <p
                  key={`G-${index}`}
                  onClick={(event) =>
                    handlePlayerListClick(
                      event.target,
                      playersInTeam.indexOf(player)
                    )
                  }
                >
                  <span className="player-jersey-number">
                    #{player.jersey_number}{" "}
                  </span>
                  <span>
                    {" "}
                    {player.last_name} {player.first_name}
                  </span>
                </p>
              ))}
          </details>
        </div>
      </div>
    </div>
  );
}
