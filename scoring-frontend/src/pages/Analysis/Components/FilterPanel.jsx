// src/components/analysis/FilterPanel.jsx
import { useEffect, useState } from "react";

export default function FilterPanel({ onApply }) {
  const [games, setGames] = useState([]);
  const [selectedGameIds, setSelectedGameIds] = useState([]);
  const [roster, setRoster] = useState([]); // merged from selected games
  const [selectedShooters, setSelectedShooters] = useState([]);

  const [showCF, setShowCF] = useState(true);
  const [showCA, setShowCA] = useState(true);
  const [showGF, setShowGF] = useState(true);
  const [showGA, setShowGA] = useState(true);

  const [strengths, setStrengths] = useState({ EV: true, PP: true, PK: true });
  const [shotTypes, setShotTypes] = useState({}); // lazy fill after data if you want

  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
  const token = sessionStorage.getItem("jwt_token");

  useEffect(() => {
    // Load games for team (you already have this endpoint)
    (async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/games/get-for-user`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        setGames(data);
      } catch (e) {
        console.error(e);
      }
    })();
  }, []);

  // When game selection changes, load rosters and merge unique players
  useEffect(() => {
    if (selectedGameIds.length === 0) {
      setRoster([]);
      return;
    }

    (async () => {
      const merged = new Map();
      for (const gid of selectedGameIds) {
        try {
          const res = await fetch(
            `${BACKEND_URL}/tagging/roster-for-game?game_id=${gid}`,
            {
              headers: { Authorization: `Bearer ${token}` },
            }
          );
          const data = await res.json();
          data.forEach((r) => {
            const p = r.player;
            if (!merged.has(p.id)) merged.set(p.id, p);
          });
        } catch (e) {
          console.error(e);
        }
      }
      setRoster(
        Array.from(merged.values()).sort(
          (a, b) => a.jersey_number - b.jersey_number
        )
      );
    })();
  }, [selectedGameIds]);

  const toggleGame = (gid) => {
    setSelectedGameIds((s) =>
      s.includes(gid) ? s.filter((x) => x !== gid) : [...s, gid]
    );
  };

  const toggleShooter = (pid) => {
    setSelectedShooters((s) =>
      s.includes(pid) ? s.filter((x) => x !== pid) : [...s, pid]
    );
  };

  const apply = () => {
    const strengthsList = Object.entries(strengths)
      .filter(([, v]) => v)
      .map(([k]) => k);
    onApply({
      game_ids: selectedGameIds,
      shooter_ids: selectedShooters,
      show_cf: showCF,
      show_ca: showCA,
      show_gf: showGF,
      show_ga: showGA,
      strengths: strengthsList,
      shot_types: Object.entries(shotTypes)
        .filter(([, v]) => v)
        .map(([k]) => k),
    });
  };

  return (
    <div className="auth-form" style={{ maxWidth: 960 }}>
      <div className="two-col">
        <div>
          <label>Games</label>
          <div className="pill-wrap">
            {games.map((g) => (
              <button
                key={g.id}
                className={`pill ${
                  selectedGameIds.includes(g.id) ? "pill-active" : ""
                }`}
                onClick={() => toggleGame(g.id)}
                type="button"
                title={`${g.date} vs ${g.opponent}`}
              >
                {g.date} {g.home ? "vs" : "@"} {g.opponent}
              </button>
            ))}
          </div>

          <label>Players (optional)</label>
          <div className="pill-wrap">
            {roster.length === 0 && (
              <div className="muted">Pick games to load roster</div>
            )}
            {roster.map((p) => (
              <button
                key={p.id}
                className={`pill ${
                  selectedShooters.includes(p.id) ? "pill-active" : ""
                }`}
                onClick={() => toggleShooter(p.id)}
                type="button"
                title={`${p.first_name} ${p.last_name}`}
              >
                {p.jersey_number} {p.last_name}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label>Include result types</label>
          <div className="grid-2">
            <Checkbox
              label="Chance For (MP +)"
              checked={showCF}
              onChange={setShowCF}
            />
            <Checkbox
              label="Chance Against (MP -)"
              checked={showCA}
              onChange={setShowCA}
            />
            <Checkbox
              label="Goal For (Maali +)"
              checked={showGF}
              onChange={setShowGF}
            />
            <Checkbox
              label="Goal Against (Maali -)"
              checked={showGA}
              onChange={setShowGA}
            />
          </div>

          <label>Strengths</label>
          <div className="grid-3">
            {["EV", "PP", "PK"].map((k) => (
              <Checkbox
                key={k}
                label={k}
                checked={strengths[k]}
                onChange={(v) => setStrengths((s) => ({ ...s, [k]: v }))}
              />
            ))}
          </div>
        </div>
      </div>

      <button onClick={apply} style={{ marginTop: 8 }}>
        Apply
      </button>
    </div>
  );
}

function Checkbox({ label, checked, onChange }) {
  return (
    <label className="chk">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span>{label}</span>
    </label>
  );
}
