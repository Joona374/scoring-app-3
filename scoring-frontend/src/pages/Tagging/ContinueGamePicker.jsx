import "./Styles/ContinueGamePicker.css"; // assume styles in a separate file

export default function ContinueGamePicker({
  pickMode,
  gamesForTeam,
  setCurrentGameId,
}) {
  return (
    <div className="game-picker-container">
      <div className="continue-game-container">
        <h2>Continue a Game</h2>
        <table className="game-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Vastustaja</th>
              <th>Pvm.</th>
              <th>Koti/Vieras</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {gamesForTeam.map((game, index) => (
              <tr key={game.id}>
                <td>{index + 1}</td>
                <td>{game.opponent}</td>
                <td>{new Date(game.date).toLocaleDateString()}</td>
                <td>{game.home ? "Koti" : "Vieras"}</td>
                <td>
                  <button
                    className="select-button"
                    onClick={() => {
                      setCurrentGameId(game.id);
                      pickMode();
                    }}
                  >
                    Valitse
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
