// src/pages/Analysis/Components/KPIs.jsx
export default function KPIs({ totals }) {
  // safe defaults if something is missing
  const shots = totals?.shots ?? 0;
  const chances = totals?.chances ?? 0;
  const goals = totals?.goals ?? 0;
  const sh = totals?.shooting_pct ?? 0;

  return (
    <div className="kpis">
      <KPI label="Laukaukset" value={shots + chances + goals} />
      <KPI label="Maalipaikat" value={chances + goals} />
      <KPI label="Maalit" value={goals} />
      <KPI label="Sh%" value={`${sh}%`} />
    </div>
  );
}

function KPI({ label, value }) {
  return (
    <div className="kpi">
      <div className="kpi-value">{value}</div>
      <div className="kpi-label">{label}</div>
    </div>
  );
}
