import CreateGame from "../CreateGame/CreateGame";
import "./Styles/GamePicker.css";

export default function GamePicker({
  setCurrentGameId,
  onCreateGame,
  onContinueGame,
}) {
  return (
    <div className="game-picker-card">
      <h1>Aloita tilastointi</h1>
      <p>Luo uusi peli tai jatka olemassa olevaa.</p>
      <div className="button-group">
        <button onClick={onCreateGame}>Luo uusi peli</button>
        <button onClick={onContinueGame}>Jatka luotua peliä</button>
      </div>
    </div>
  );
}
