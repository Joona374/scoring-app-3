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
      alert("No position selected");
    }
  };

  return (
    <div className="roster-selector-wrapepr">
      <h3>This is roster selector :ddD</h3>
      <div className="roster-selector">
        <div className="lineup">
          <div className="left-roster-column">
            {["1", "2", "3", "4"].map((num) => {
              return (
                <div className="positions-row" key={`${num}-DROW`}>
                  {[`${num}-LD`, `${num}-RD`].map((position_id) => {
                    const rosterSpot = playersInRoster.find(
                      (spot) => `${spot.line}-${spot.position}` === position_id
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
                      />
                    );
                  })}
                </div>
              );
            })}

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
                  />
                );
              })}
            </div>
          </div>
          <div className="right-roster-column">
            {["1", "2", "3", "4", "5"].map((num) => {
              return (
                <div className="positions-row" key={`${num}-FROW`}>
                  {[`${num}-LW`, `${num}-C`, `${num}-RW`].map((position_id) => {
                    const rosterSpot = playersInRoster.find(
                      (spot) => `${spot.line}-${spot.position}` === position_id
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
                      />
                    );
                  })}
                </div>
              );
            })}
          </div>
        </div>
        <div className="player-list">
          {players.map((player, index) => {
            return (
              <p
                key={index}
                onClick={(event) => handlePlayerListClick(event.target, index)}
              >
                {index + 1}. {player.first_name} {player.last_name}{" "}
                {player.position}
              </p>
            );
          })}
        </div>
      </div>

      <button onClick={() => setShowRosterSelector(false)}>Hide</button>
    </div>
  );
}
