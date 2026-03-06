import "./PlayerKPIs.css";
import InfoTooltip from "./InfoTooltip";

export default function PlayerKPIs({ summary }) {
  const kpis = [
    { label: "Pelit", value: summary.games_played },
    { label: "Maalit", value: summary.goals },
    { label: "Maalipaikat (MP)", value: summary.chances },
    { label: "Tehokkuus (MP%)", value: `${summary.efficiency}%` },
    { label: "MP / Peli", value: summary.chances_per_game },
  ];

  const plusMinus = [
    { label: "M +/- (osall.) / peli", value: summary.participation_m_diff },
    { label: "MP +/- (osall.) / peli", value: summary.participation_mp_diff },
    { label: "M +/- (jää) / peli", value: summary.on_ice_m_diff },
    { label: "MP +/- (jää) / peli", value: summary.on_ice_mp_diff },
  ];

  const getPlusMinusClass = (val) => {
    if (val > 0) return "stat-positive";
    if (val < 0) return "stat-negative";
    return "";
  };

  const formatPlusMinus = (val) => {
    if (val > 0) return `+${val}`;
    return val;
  };

  return (
    <section className="player-kpis-section">
      <div className="section-header-row info-row">
        <h3 className="section-title-small">Kauden yhteenveto</h3>
        <InfoTooltip text="Keskeiset suoritusarvot valitulla aikavälillä. +/- tilastot on suhteutettu pelattujen otteluiden määrään (per peli)." />
      </div>
      
      <div className="kpi-row main-stats">
        {kpis.map((kpi, i) => (
          <div key={i} className="player-kpi-card">
            <span className="player-kpi-value">{kpi.value}</span>
            <span className="player-kpi-label">{kpi.label}</span>
          </div>
        ))}
      </div>
      <div className="kpi-row plus-minus-stats">
        {plusMinus.map((kpi, i) => (
          <div key={i} className="player-kpi-card">
            <span className={`player-kpi-value ${getPlusMinusClass(kpi.value)}`}>
              {formatPlusMinus(kpi.value)}
            </span>
            <span className="player-kpi-label">{kpi.label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
