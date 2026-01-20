// src/pages/Analysis/Components/FilterAccordion.jsx
import { useEffect, useMemo, useState } from "react";

export default function FilterAccordion({ onApply }) {
  const [open, setOpen] = useState(false);

  const [games, setGames] = useState([]);
  const [selectedGameIds, setSelectedGameIds] = useState([]);

  const [teamPlayers, setTeamPlayers] = useState([]);
  const [selectedShooters, setSelectedShooters] = useState([]);

  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
  const token = sessionStorage.getItem("jwt_token");
  const PLAYERS_FOR_TEAM_ENDPOINT = `${BACKEND_URL}/players/for-team`;

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/games/get-for-user`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        setGames(data);
      } catch (e) {
        console.error("Failed to load games", e);
      }
    })();

    (async () => {
      try {
        const res = await fetch(PLAYERS_FOR_TEAM_ENDPOINT, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        data.sort((a, b) => a.jersey_number - b.jersey_number);
        setTeamPlayers(data);
      } catch (e) {
        console.error("Failed to load team players", e);
      }
    })();
  }, []);

  const gameIdsAll = useMemo(() => games.map((g) => g.id), [games]);
  const playerIdsAll = useMemo(
    () => teamPlayers.map((p) => p.id),
    [teamPlayers]
  );

  const toggle = (arr, setArr, id) =>
    setArr(arr.includes(id) ? arr.filter((x) => x !== id) : [...arr, id]);

  const apply = () => {
    if (selectedGameIds.length === 0) return; // must pick at least one game
    onApply({ game_ids: selectedGameIds, shooter_ids: selectedShooters });
    setOpen(false);
  };

  // Format helpers
  const fmtPlayer = (p) =>
    `#${p.jersey_number} ${p.last_name} ${
      p.first_name ? p.first_name.slice(0, 1) : ""
    }.`;
  const fmtGame = (g) => `${g.date} ${g.home ? "vs" : "@"} ${g.opponent}`;

  // First-pill labels
  const gamesFirstPillLabel =
    selectedGameIds.length === 0 ? "Kaikki" : "Nollaa";
  const playersFirstPillLabel =
    selectedShooters.length === 0 ? "Kaikki" : "Nollaa";

  // First-pill actions
  const handleGamesFirstPill = () => {
    if (selectedGameIds.length === 0) setSelectedGameIds(gameIdsAll); // All
    else setSelectedGameIds([]); // Reset
  };
  const handlePlayersFirstPill = () => {
    if (selectedShooters.length === 0) setSelectedShooters(playerIdsAll); // All
    else setSelectedShooters([]); // Reset
  };

  const disableApply = selectedGameIds.length === 0;

  return (
    <div className="accordion">
      <button className="accordion-toggle" onClick={() => setOpen((o) => !o)}>
        {open
          ? "▲ Suodattimet (Pelit & Pelaajat)"
          : "▼ Suodattimet (Pelit & Pelaajat)"}
      </button>

      {open && (
        <div className="accordion-body">
          <div className="two-col compact">
            {/* Games */}
            <div>
              <div className="section-title">Pelit</div>
              <div className="pill-wrap tight">
                <button
                  className={`pill sm ${
                    selectedGameIds.length === 0 ? "" : "pill-active"
                  }`}
                  onClick={handleGamesFirstPill}
                  type="button"
                  disabled={games.length === 0}
                  title={gamesFirstPillLabel}
                >
                  {gamesFirstPillLabel}
                </button>

                {games.map((g) => (
                  <button
                    key={g.id}
                    className={`pill sm ${
                      selectedGameIds.includes(g.id) ? "pill-active" : ""
                    }`}
                    onClick={() =>
                      toggle(selectedGameIds, setSelectedGameIds, g.id)
                    }
                    type="button"
                    title={fmtGame(g)}
                  >
                    {fmtGame(g)}
                  </button>
                ))}
              </div>
            </div>

            {/* Players */}
            <div>
              <div className="section-title">Pelaajat</div>
              <div className="pill-wrap tight">
                <button
                  className={`pill sm ${
                    selectedShooters.length === 0 ? "" : "pill-active"
                  }`}
                  onClick={handlePlayersFirstPill}
                  type="button"
                  disabled={teamPlayers.length === 0}
                  title={playersFirstPillLabel}
                >
                  {playersFirstPillLabel}
                </button>

                {teamPlayers.length === 0 && (
                  <div className="muted">Joukkueelle ei löytynyt pelaajia</div>
                )}

                {teamPlayers.map((p) => (
                  <button
                    key={p.id}
                    className={`pill sm ${
                      selectedShooters.includes(p.id) ? "pill-active" : ""
                    }`}
                    onClick={() =>
                      toggle(selectedShooters, setSelectedShooters, p.id)
                    }
                    type="button"
                    title={fmtPlayer(p)}
                  >
                    {fmtPlayer(p)}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="accordion-actions">
            <button
              className="btn"
              onClick={apply}
              disabled={disableApply}
              title={
                disableApply
                  ? "Valitse vähintään yksi peli"
                  : "Käytä suodattimia"
              }
            >
              Valitse
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
