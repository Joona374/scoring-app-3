import "./PlayerFilters.css";

export default function PlayerFilters({ 
  filters, 
  setFilters, 
  availableGamesCount 
}) {
  const situations = [
    { label: "Kaikki", value: "ALL" },
    { label: "5v5", value: "ES" },
    { label: "YV", value: "PP" },
    { label: "AV", value: "PK" },
  ];

  const venues = [
    { label: "Kaikki", value: "ALL" },
    { label: "Koti", value: "HOME" },
    { label: "Vieras", value: "AWAY" },
  ];

  return (
    <section className="player-filters-section">
      <div className="filter-group">
        <span className="filter-label">Tilanne</span>
        <div className="filter-buttons">
          {situations.map((sit) => (
            <button
              key={sit.value}
              className={`filter-btn ${filters.situation === sit.value ? "active" : ""}`}
              onClick={() => setFilters({ ...filters, situation: sit.value })}
            >
              {sit.label}
            </button>
          ))}
        </div>
      </div>

      <div className="filter-group">
        <span className="filter-label">Paikka</span>
        <div className="filter-buttons">
          {venues.map((v) => (
            <button
              key={v.value}
              className={`filter-btn ${filters.venue === v.value ? "active" : ""}`}
              onClick={() => setFilters({ ...filters, venue: v.value })}
            >
              {v.label}
            </button>
          ))}
        </div>
      </div>

      <div className="filter-group slider-group">
        <span className="filter-label">Viimeiset pelit</span>
        <div className="slider-container">
          <input
            type="range"
            min="1"
            max={Math.max(availableGamesCount, 1)}
            value={filters.lastGames || availableGamesCount}
            onChange={(e) => setFilters({ ...filters, lastGames: parseInt(e.target.value) })}
            className="games-slider"
          />
          <span className="slider-value">
            {filters.lastGames || availableGamesCount} / {availableGamesCount} peliä
          </span>
        </div>
      </div>

      <div className="filter-group date-group">
        <span className="filter-label">Aikaväli</span>
        <div className="date-inputs">
          <input
            type="date"
            value={filters.startDate || ""}
            onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
            className="date-input"
          />
          <span className="date-separator">-</span>
          <input
            type="date"
            value={filters.endDate || ""}
            onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
            className="date-input"
          />
        </div>
      </div>
      
      <button 
        className="reset-filters-btn"
        onClick={() => setFilters({
          situation: "ALL",
          venue: "ALL",
          lastGames: availableGamesCount,
          startDate: null,
          endDate: null
        })}
      >
        Nollaa suodattimet
      </button>
    </section>
  );
}
