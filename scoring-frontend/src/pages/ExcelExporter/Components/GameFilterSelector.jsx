import "./GameFilterSelector.css";

export default function ({ game, gamesSelected, setGamesSelected }) {
  const changeCheckbox = (gameId) => {
    if (gamesSelected.includes(gameId)) {
      const newGames = gamesSelected.filter((id) => id !== gameId);
      console.log(newGames);

      setGamesSelected(newGames);
    } else {
      const newGames = [...gamesSelected, gameId];
      console.log(newGames);
      setGamesSelected(newGames);
    }
  };

  console.log("game in component", game);
  return (
    <tr className="game-row">
      <td>
        <input
          type="checkbox"
          checked={gamesSelected.includes(game.id)}
          onChange={() => changeCheckbox(game.id)}
        />
      </td>
      <td>
        <p>{game.date}</p>
      </td>
      <td>
        <p>{game.opponent}</p>
      </td>
      <td>{game.home ? "Koti" : "Vieras"}</td>
    </tr>
  );
}
