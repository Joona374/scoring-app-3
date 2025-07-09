import CreateGame from "../CreateGame/CreateGame";

export default function GamePicker({
  setCurrentGameId,
  onCreateGame,
  onContinueGame,
}) {
  return (
    <div>
      <button onClick={onCreateGame}>Create a new game</button>
      <button onClick={onContinueGame}>Continue a game</button>
    </div>
  );
}
