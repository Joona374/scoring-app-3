import { useEffect, useState } from "react";
import "./Styles/RosterSelector.css";
import RosterBox from "./RosterBox";

export default function RosterSelector({
  setShowRosterSelector,
  players,
  playersInRoster,
  setPlayersInRoster,
}) {
  const [selectingPosition, setSelectingPosition] = useState("");

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
    console.log(line, position);
    const newPlayersInRoster = playersInRoster.map((rosterSpot, idx) => {
      if (rosterSpot.line === line && rosterSpot.position === position) {
        console.log("Do this match ever?");
        const editedRosterSpot = { ...rosterSpot, player: null };
        return editedRosterSpot;
      }
      return rosterSpot;
    });
    console.log(newPlayersInRoster);
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
