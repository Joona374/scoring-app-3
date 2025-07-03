export default function CreateGameForm({
  opponent,
  setOpponent,
  setGameDate,
  setHomeGame,
  setShowRosterSelector,
  submitGame,
}) {
  const changeHomeRadio = (new_value) => {
    setHomeGame(new_value === "home");
  };

  return (
    <form onSubmit={submitGame}>
      <label htmlFor="opponent-input">Opponent</label>
      <input
        id="opponent-input"
        value={opponent}
        onChange={(e) => setOpponent(e.target.value)}
        type="text"
        placeholder="Opponent..."
      />

      <label htmlFor="date-input">Date:</label>
      <input
        type="date"
        id="date-input"
        onChange={(e) => setGameDate(e.target.value)}
      />

      <fieldset>
        <legend>Game Location</legend>
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
            <label htmlFor="home-input">Home</label>
          </div>
          <div className="radio-option">
            <input
              type="radio"
              name="game-location"
              id="away-input"
              value="away"
              onChange={(e) => changeHomeRadio(e.target.value)}
            />
            <label htmlFor="away-input">Away</label>
          </div>
        </div>
      </fieldset>
      <button type="button" onClick={() => setShowRosterSelector(true)}>
        Pick roster
      </button>
      <button>Submit</button>
    </form>
  );
}
