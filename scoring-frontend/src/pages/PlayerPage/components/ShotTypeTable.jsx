import { useState, useMemo } from "react";
import "./ShotTypeTable.css";
import InfoTooltip from "./InfoTooltip";

export default function ShotTypeTable({ shotTypeStats, totalGoals, totalChances }) {
  const [sortConfig, setSortConfig] = useState({ key: "goals", direction: "desc" });

  const extendedStats = useMemo(() => {
    return shotTypeStats.map(stat => ({
      ...stat,
      goalsPct: totalGoals > 0 ? Math.round((stat.goals / totalGoals) * 1000) / 10 : 0,
      chancesPct: totalChances > 0 ? Math.round((stat.chances / totalChances) * 1000) / 10 : 0,
    }));
  }, [shotTypeStats, totalGoals, totalChances]);

  const sortedStats = useMemo(() => {
    const sorted = [...extendedStats].sort((a, b) => {
      const aVal = a[sortConfig.key];
      const bVal = b[sortConfig.key];
      if (typeof aVal === "string") {
        return sortConfig.direction === "asc" 
          ? aVal.localeCompare(bVal) 
          : bVal.localeCompare(aVal);
      }
      return sortConfig.direction === "asc" ? aVal - bVal : bVal - aVal;
    });
    return sorted;
  }, [extendedStats, sortConfig]);

  const requestSort = (key) => {
    let direction = "desc";
    if (sortConfig.key === key && sortConfig.direction === "desc") {
      direction = "asc";
    }
    setSortConfig({ key, direction });
  };

  const renderHeader = (label, key) => {
    const isActive = sortConfig.key === key;
    return (
      <th onClick={() => requestSort(key)} className="sortable">
        <div className="header-content">
          <span>{label}</span>
          <span className={`sort-arrow ${isActive ? "active" : ""}`}>
            {sortConfig.direction === "desc" ? "▼" : "▲"}
          </span>
        </div>
      </th>
    );
  };

  return (
    <section className="shot-type-section">
      <div className="section-header-row info-row">
        <h3 className="section-title-small">Laukaustyypit</h3>
        <InfoTooltip text="Tilastot eri laukaustyypeistä. % M kertoo osuuden kaikista tehdyistä maaleista ja % P osuuden kaikista maalipaikoista." />
      </div>
      
      <div className="table-container-small">
        <table className="shot-type-table">
          <thead>
            <tr>
              {renderHeader("Tyyppi", "shot_type")}
              {renderHeader("Maalit", "goals")}
              {renderHeader("% M", "goalsPct")}
              {renderHeader("Paikat", "chances")}
              {renderHeader("% P", "chancesPct")}
              {renderHeader("Teho", "efficiency")}
            </tr>
          </thead>
          <tbody>
            {sortedStats.length > 0 ? (
              sortedStats.map((stat, index) => (
                <tr key={index}>
                  <td className="shot-type-name">{stat.shot_type}</td>
                  <td>{stat.goals}</td>
                  <td className="stat-pct">{stat.goalsPct}%</td>
                  <td>{stat.chances}</td>
                  <td className="stat-pct">{stat.chancesPct}%</td>
                  <td className={stat.efficiency > 15 ? "stat-positive" : ""}>
                    {stat.efficiency}%
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={6} className="no-data">Ei laukaustietoja</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
