import "./Styles/MiniRosterView.css";

export default function MiniRosterView({ playersInRoster }) {
  const getNum = (lineIdx, pos) => {
    const rosterSpot = playersInRoster.find(
      (p) => p.line === lineIdx && p.position === pos
    );
    if (!rosterSpot) return "--";
    const player = rosterSpot.player;
    if (!player) return "--";

    // if (player.jersey_number < 10) return `${player.jersey_number} `;

    // return player.jersey_number;

    return player.last_name;
  };

  return (
    <div className="mini-roster-view">
      <h3 style={{ textAlign: "center" }}>Kokoonpano</h3>
      <div className="mini-forwards-list">
        <p className="mini-roster-title">Hyökkääjät:</p>
        {[...Array(5)].map((_, i) => (
          <div className="forwards-row">
            <span className="player-number">{getNum(i + 1, "LW")}</span>
            <span className="player-number">{getNum(i + 1, "C")}</span>
            <span className="player-number">{getNum(i + 1, "RW")}</span>
          </div>
        ))}
      </div>
      <hr />

      <div className="mini-defenders-list">
        <p className="mini-roster-title">Puolustajat:</p>
        {[...Array(4)].map((_, i) => (
          <div key={i} className="defenders-row">
            <span className="player-number">{getNum(i + 1, "LD")}</span>
            <span className="player-number">{getNum(i + 1, "RD")}</span>
          </div>
        ))}
      </div>
      <hr />

      <p className="mini-roster-title">Maalivahdit:</p>

      <div className="goalies-row">
        <span className="player-number">{getNum(1, "G")}</span>
        <span className="player-number">{getNum(2, "G")}</span>
      </div>
    </div>
  );
}
