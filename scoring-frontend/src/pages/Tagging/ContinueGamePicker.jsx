export default function ContinueGamePicker({ gamesForTeam, setCurrentGameId }) {
  return (
    <div>
      {gamesForTeam.map((game, index) => {
        return (
          <button key={index} onClick={() => setCurrentGameId(game.id)}>
            {game.opponent} {game.date}
          </button>
        );
      })}
    </div>
  );
}
