import "../../components/FormStyles.css";

export default function CreateGameForm({
  opponent,
  setOpponent,
  setGameDate,
  setHomeGame,
  showRosterSelector,
  setShowRosterSelector,
  submitGame,
  onCancel,
}) {
  const changeHomeRadio = (new_value) => {
    setHomeGame(new_value === "home");
  };

  return (
    <form className="auth-form" onSubmit={submitGame}>
      <label htmlFor="opponent-input">Vastustaja</label>
      <input
        id="opponent-input"
        value={opponent}
        onChange={(e) => setOpponent(e.target.value)}
        type="text"
        placeholder="Opponent..."
      />

      <label htmlFor="date-input">Päivämäärä:</label>
      <input
        type="date"
        id="date-input"
        onChange={(e) => setGameDate(e.target.value)}
      />

      <fieldset>
        <legend>Koti/Vieras</legend>
        <div className="radio-group">
          <div className="radio-option">
            {" "}
            <input
              type="radio"
              name="game-location"
              id="home-input"
              value="home"
              onChange={(e) => changeHomeRadio(e.target.value)}
            />
            <label htmlFor="home-input">Koti</label>
          </div>
          <div className="radio-option">
            <input
              type="radio"
              name="game-location"
              id="away-input"
              value="away"
              onChange={(e) => changeHomeRadio(e.target.value)}
            />
            <label htmlFor="away-input">Vieras</label>
          </div>
        </div>
      </fieldset>
      <button
        type="button"
        className={"secondary-button"}
        onClick={() => setShowRosterSelector(!showRosterSelector)}
      >
        Valitse kokoonpano
      </button>
      <button>Jatka</button>
      <button onClick={onCancel} className={"cancel-button"}>
        Peruuta
      </button>
    </form>
  );
}
