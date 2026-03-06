import { useState, useMemo } from "react";
import "./GameLogTable.css";
import InfoTooltip from "./InfoTooltip";

export default function GameLogTable({ gameLog, summary }) {
  const [sortConfig, setSortConfig] = useState({ key: "date", direction: "desc" });

  const sortedLog = useMemo(() => {
    return [...gameLog].sort((a, b) => {
      const aVal = a[sortConfig.key];
      const bVal = b[sortConfig.key];
      if (typeof aVal === "string") {
        return sortConfig.direction === "asc" 
          ? aVal.localeCompare(bVal) 
          : bVal.localeCompare(aVal);
      }
      return sortConfig.direction === "asc" ? aVal - bVal : bVal - aVal;
    });
  }, [gameLog, sortConfig]);

  const requestSort = (key) => {
    let direction = "desc";
    if (sortConfig.key === key && sortConfig.direction === "desc") {
      direction = "asc";
    }
    setSortConfig({ key, direction });
  };

  const getSortIndicator = (key) => {
    if (sortConfig.key !== key) return "";
    return sortConfig.direction === "desc" ? " ▼" : " ▲";
  };

  const getPerfClass = (val, avg) => {
    if (val > avg) return "perf-above";
    if (val < avg) return "perf-below";
    return "";
  };

  return (
    <section className="game-log-section">
      <div className="section-header-row info-row">
        <h3 className="section-title-small">Otteluhistoria</h3>
        <InfoTooltip text="Yksityiskohtainen historia pelaajan otteluista. Värikoodaus (vihreä/punainen) kertoo onko suoritus ollut pelaajan kauden keskiarvoa parempi vai huonompi." />
      </div>
      
      <div className="table-container">
        <table className="game-log-table">
          <thead>
            <tr>
              <th onClick={() => requestSort("date")} className="sortable">Pvm {getSortIndicator("date")}</th>
              <th onClick={() => requestSort("opponent")} className="sortable">Vastustaja {getSortIndicator("opponent")}</th>
              <th onClick={() => requestSort("home")} className="sortable">Paikka {getSortIndicator("home")}</th>
              <th onClick={() => requestSort("goals")} className="sortable">M {getSortIndicator("goals")}</th>
              <th onClick={() => requestSort("chances")} className="sortable">MP {getSortIndicator("chances")}</th>
              <th onClick={() => requestSort("efficiency")} className="sortable">Teho % {getSortIndicator("efficiency")}</th>
              <th onClick={() => requestSort("part_m_diff")} className="sortable">M +/- (osall.) {getSortIndicator("part_m_diff")}</th>
              <th onClick={() => requestSort("part_mp_diff")} className="sortable">MP +/- (osall.) {getSortIndicator("part_mp_diff")}</th>
              <th onClick={() => requestSort("onice_m_diff")} className="sortable">M +/- (jää) {getSortIndicator("onice_m_diff")}</th>
              <th onClick={() => requestSort("onice_mp_diff")} className="sortable">MP +/- (jää) {getSortIndicator("onice_mp_diff")}</th>
            </tr>
          </thead>
          <tbody>
            {sortedLog.map((game, i) => (
              <tr key={i}>
                <td className="date-cell">{new Date(game.date).toLocaleDateString("fi-FI")}</td>
                <td className="opponent-cell">{game.opponent}</td>
                <td className="venue-cell">{game.home ? "Koti" : "Vieras"}</td>
                <td className={getPerfClass(game.goals, summary.goals / summary.games_played)}>
                  {game.goals}
                </td>
                <td className={getPerfClass(game.chances, summary.chances / summary.games_played)}>
                  {game.chances}
                </td>
                <td className={getPerfClass(game.efficiency, summary.efficiency)}>
                  {game.efficiency}%
                </td>
                <td className={game.part_m_diff > 0 ? "stat-positive" : (game.part_m_diff < 0 ? "stat-negative" : "")}>
                  {game.part_m_diff > 0 ? `+${game.part_m_diff}` : game.part_m_diff}
                </td>
                <td className={game.part_mp_diff > 0 ? "stat-positive" : (game.part_mp_diff < 0 ? "stat-negative" : "")}>
                  {game.part_mp_diff > 0 ? `+${game.part_mp_diff}` : game.part_mp_diff}
                </td>
                <td className={game.onice_m_diff > 0 ? "stat-positive" : (game.onice_m_diff < 0 ? "stat-negative" : "")}>
                  {game.onice_m_diff > 0 ? `+${game.onice_m_diff}` : game.onice_m_diff}
                </td>
                <td className={game.onice_mp_diff > 0 ? "stat-positive" : (game.onice_mp_diff < 0 ? "stat-negative" : "")}>
                  {game.onice_mp_diff > 0 ? `+${game.onice_mp_diff}` : game.onice_mp_diff}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
