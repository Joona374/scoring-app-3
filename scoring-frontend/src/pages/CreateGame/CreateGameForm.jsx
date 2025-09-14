import "../../components/FormStyles.css";
import MutedButton from "../../components/MutedButton/MutedButton";
import LoadingSpinner from "../../components/LoadingSpinner/LoadingSpinner";

export default function CreateGameForm({
  opponent,
  setOpponent,
  setGameDate,
  setHomeGame,
  setPowerplays,
  setPenaltyKills,
  powerplays,
  penaltyKills,
  showRosterSelector,
  setShowRosterSelector,
  submitGame,
  onCancel,
  isLoadingCreateGame,
  setIsLoadingCreateGame,
}) {
  const changeHomeRadio = (new_value) => {
    setHomeGame(new_value === "home");
  };

  return (
    <div className="create-game-form">
      <form className="auth-form" onSubmit={submitGame}>
        <label htmlFor="opponent-input">Vastustaja</label>
        <input
          id="opponent-input"
          value={opponent}
          onChange={(e) => setOpponent(e.target.value)}
          type="text"
          placeholder="Opponent..."
          required
        />

        <label htmlFor="date-input">Päivämäärä:</label>
        <input
          type="date"
          id="date-input"
          onChange={(e) => setGameDate(e.target.value)}
          required
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
                required
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
                required
              />
              <label htmlFor="away-input">Vieras</label>
            </div>
          </div>
        </fieldset>

        {/* Erikoistilanteet with ylivoima and alivoima input sideby side not on top of eachother */}
        <div className="special-teams-inputs">
          <div className="special-team-input">
            <label htmlFor="powerplays-input">Ylivoimat</label>
            <input
              id="powerplays-input"
              value={powerplays}
              onChange={(e) => setPowerplays(e.target.value)}
              type="number"
              min="0"
              placeholder="0"
            />
          </div>
          <div className="special-team-input">
            <label htmlFor="penaltykills-input">Alivoimat</label>
            <input
              id="penaltykills-input"
              value={penaltyKills}
              onChange={(e) => setPenaltyKills(e.target.value)}
              type="number"
              min="0"
              placeholder="0"
            />
          </div>
        </div>

        <button
          type="button"
          className={"secondary-button"}
          onClick={() => setShowRosterSelector(!showRosterSelector)}
        >
          Valitse kokoonpano
        </button>
        <button type="submit" disabled={isLoadingCreateGame}>
          {isLoadingCreateGame ? LoadingSpinner(18) : "Luo peli"}
        </button>
      </form>
    </div>
  );
}
