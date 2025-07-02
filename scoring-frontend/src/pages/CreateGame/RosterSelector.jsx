import { useEffect, useState } from "react";
import "./Styles/RosterSelector.css";
import RosterBox from "./RosterBox";

export default function RosterSelector({ setShowRosterSelector, players }) {
  const generateEmptyPlayersInRoster = () => {
    let emptyPlayersInRoster = [];
    for (let i = 1; i <= 5; i++) {
      ["LW", "C", "RW"].map((position) =>
        emptyPlayersInRoster.push({ line: i, position: position, player: null })
      );
    }
    for (let i = 1; i <= 4; i++) {
      ["LD", "RD"].map((position) =>
        emptyPlayersInRoster.push({ line: i, position: position, player: null })
      );
    }
    for (let i = 1; i <= 2; i++) {
      ["G"].map((position) =>
        emptyPlayersInRoster.push({ line: i, position: position, player: null })
      );
    }

    return emptyPlayersInRoster;
  };

  const [selectingPosition, setSelectingPosition] = useState("");
  const [playersInRoster, setPlayersInRoster] = useState(
    generateEmptyPlayersInRoster()
  );

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

      const selectedBox = document.getElementById(selectingPosition);
      selectedBox.innerText = `${player.first_name} ${player.last_name}`;
    } else {
      alert("No position selected");
    }
  };

  return (
    <div className="roster-selector-wrapepr">
      <h3>This is roster selector :ddD</h3>
      <div className="roster-selector">
        <div className="lineup">
          <div className="left-column">
            {["1", "2", "3", "4"].map((num) => {
              return (
                <div className="positions-row" key={`${num}-DROW`}>
                  {[`${num}-LD`, `${num}-RD`].map((position_id) => {
                    return (
                      <RosterBox
                        id={position_id}
                        key={position_id}
                        selectingPosition={selectingPosition}
                        setSelectingPosition={setSelectingPosition}
                      />
                    );
                  })}
                </div>
              );
            })}

            <div className="goalies-row">
              <RosterBox
                id="1-G"
                selectingPosition={selectingPosition}
                setSelectingPosition={setSelectingPosition}
              />
              <RosterBox
                id="2-G"
                selectingPosition={selectingPosition}
                setSelectingPosition={setSelectingPosition}
              />
            </div>
          </div>
          <div className="right-column">
            {["1", "2", "3", "4", "5"].map((num) => {
              return (
                <div className="positions-row" key={`${num}-FROW`}>
                  {[`${num}-LW`, `${num}-C`, `${num}-RW`].map((position_id) => {
                    return (
                      <RosterBox
                        id={position_id}
                        key={position_id}
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
