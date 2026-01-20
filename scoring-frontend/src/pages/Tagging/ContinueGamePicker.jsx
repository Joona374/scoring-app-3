import "./Styles/ContinueGamePicker.css"; // assume styles in a separate file
import BasicButton from "../../components/BasicButton/BasicButton";
import MutedButton from "../../components/MutedButton/MutedButton";
import LoadingSpinner from "../../components/LoadingSpinner/LoadingSpinner";
import ScrollContainer from "../../components/ScrollContainer/ScrollContainer";
import { useEffect, useState } from "react";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function ContinueGamePicker({
  pickMode,
  gamesForTeam,
  setGamesForTeam,
  setCurrentGameId,
  onReturn,
  fetchGamesForTeam,
}) {
  useEffect(() => {
    fetchGamesForTeam();
  }, []);

  const [deletingGameId, setDeletingGameId] = useState(null);

  const firstConfirmDeletingGameWithTags = (game) => {
    const confirmed = window.confirm(
      `Oletko varma että haluat poistaa tämän pelin?\n${
        game.opponent
      } - ${new Date(game.date).toLocaleDateString()} - ${
        game.home ? "Koti" : "Vieras"
      }`
    );
    return confirmed;
  };

  const secondConfirmDeletingGameWithTags = (
    teamTags,
    playerTags,
    goalieTags
  ) => {
    const confirmed = window.confirm(
      `Oletko varma että haluat poistaa pelin? Poistamalla pelin poistat myös kaikki merkatut maalipaikat. Peliin on jo merkattu\n
      ${teamTags} Joukkuetilasto tägiä\n
      ${playerTags} Pelaajatilasto tägiä\n
      ${goalieTags} Maalivahtitilasto tägiä\n
      `
    );
    return confirmed;
  };

  const removeGameFromList = (deletedGame) => {
    const newGamesForTeam = gamesForTeam.filter(
      (game) => game.id !== deletedGame.id
    );
    setGamesForTeam(newGamesForTeam);
  };

  async function deleteGame(game, alreadyConfirmed) {
    const token = sessionStorage.getItem("jwt_token");
    if (game == null) return;
    setDeletingGameId(game.id);

    if (!alreadyConfirmed) {
      const firstConfirm = firstConfirmDeletingGameWithTags(game);
      if (!firstConfirm) {
        setDeletingGameId(null);
        return;
      }
    }

    const response = await fetch(
      `${BACKEND_URL}/games/delete/${game.id}?already_confirmed=${alreadyConfirmed}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (response.ok) {
      const data = await response.json();
      setDeletingGameId(null);

      if (data.challenge === true && !alreadyConfirmed) {
        const secondConfirm = secondConfirmDeletingGameWithTags(
          data.team_tags,
          data.player_tags,
          data.goalie_tags
        );
        if (!secondConfirm) {
          setDeletingGameId(null);
        } else deleteGame(game, true);

        return;
      } else if (data.success === true) {
        removeGameFromList(game);
        setDeletingGameId(null);
      }
    } else {
      console.error("Failed to delete game");
      setDeletingGameId(null);
    }
  }

  return (
    <div className="game-picker-container">
      <div className="continue-game-container">
        <h2>
          {" "}
          {gamesForTeam.length === 0 ? "Ladataan pelejä..." : "Valitse peli"}
        </h2>
        {gamesForTeam.length === 0 ? (
          LoadingSpinner(200)
        ) : (
          <ScrollContainer className="table-wrapper">
            <table className="game-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Vastustaja</th>
                  <th>Pvm.</th>
                  <th>Koti/Vieras</th>
                  <th>Valitse</th>
                  <th>Poista</th>
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
                    <td>
                      <button
                        className="select-button"
                        onClick={() => {
                          deleteGame(game, false);
                        }}
                      >
                        {deletingGameId === game.id
                          ? LoadingSpinner(18)
                          : "Poista"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </ScrollContainer>
        )}
      </div>
      <MutedButton
        text="Takaisin"
        onClickMethod={() => onReturn()}
      ></MutedButton>
    </div>
  );
}
