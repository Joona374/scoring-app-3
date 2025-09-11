import { useEffect, useState } from "react";
import "./Styles/RosterSelector.css";
import RosterBox from "./RosterBox";
import LoadingSpinner from "../../components/LoadingSpinner/LoadingSpinner";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function RosterSelector({
  setShowRosterSelector,
  players,
  playersInRoster,
  setPlayersInRoster,
}) {
  const [selectingPosition, setSelectingPosition] = useState("");
  const [scraperUrl, setScraperUrl] = useState("");
  const [scraperLocation, setScraperLocation] = useState("koti");
  const [isLoadingScrapedRoster, setIsLoadingScrapedRoster] = useState(false);

  const handlePlayerListClick = (target, index) => {
    if (selectingPosition) {
      const player = players[index];

      const [line, position] = selectingPosition.split("-");
      const rosterSpotIndex = playersInRoster.findIndex(
        (spot) => spot.line === parseInt(line) && spot.position === position
      );
      let newPlayersInRoster = playersInRoster.map((spot, index) => {
        if (index === rosterSpotIndex) {
          return { ...spot, player: player };
        }
        return spot;
      });
      setPlayersInRoster(newPlayersInRoster);

      if (rosterSpotIndex < 24) {
        const nextSpot = playersInRoster[rosterSpotIndex + 1];
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
    const newPlayersInRoster = playersInRoster.map((rosterSpot, idx) => {
      if (rosterSpot.line === line && rosterSpot.position === position) {
        const editedRosterSpot = { ...rosterSpot, player: null };
        return editedRosterSpot;
      }
      return rosterSpot;
    });
    setPlayersInRoster(newPlayersInRoster);
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
        const matchedPlayer = players.find((p) => p.id === player.id);
        return {
          line: parseInt(line),
          position: position,
          player: matchedPlayer || null,
        };
      }
    );

    setPlayersInRoster(newPlayersInRoster);
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
                      const rosterSpot = playersInRoster.find(
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
                        const rosterSpot = playersInRoster.find(
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
              const rosterSpot = playersInRoster.find(
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

          <form onSubmit={handleScraperSubmit} className="scraper-roster-input">
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
        <div className="player-list">
          <details open>
            <summary>Hyökkääjät</summary>
            {players
              .filter((p) => p.position === "FORWARD")
              .sort((a, b) => a.last_name.localeCompare(b.last_name))
              .map((player, index) => (
                <p
                  key={`F-${index}`}
                  onClick={(event) =>
                    handlePlayerListClick(event.target, players.indexOf(player))
                  }
                >
                  #{player.jersey_number} {player.last_name} {player.first_name}
                </p>
              ))}
          </details>

          <details open>
            <summary>Puolustajat</summary>
            {players
              .filter((p) => p.position === "DEFENDER")
              .sort((a, b) => a.last_name.localeCompare(b.last_name))
              .map((player, index) => (
                <p
                  key={`D-${index}`}
                  onClick={(event) =>
                    handlePlayerListClick(event.target, players.indexOf(player))
                  }
                >
                  #{player.jersey_number} {player.first_name} {player.last_name}
                </p>
              ))}
          </details>

          <details open>
            <summary>Maalivahdit</summary>
            {players
              .filter((p) => p.position === "GOALIE")
              .sort((a, b) => a.last_name.localeCompare(b.last_name))
              .map((player, index) => (
                <p
                  key={`G-${index}`}
                  onClick={(event) =>
                    handlePlayerListClick(event.target, players.indexOf(player))
                  }
                >
                  #{player.jersey_number} {player.first_name} {player.last_name}
                </p>
              ))}
          </details>
        </div>
      </div>
    </div>
  );
}
