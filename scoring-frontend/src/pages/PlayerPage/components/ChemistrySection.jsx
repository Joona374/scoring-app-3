import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ZAxis,
  LabelList,
  ReferenceLine
} from "recharts";
import "./ChemistrySection.css";

export default function ChemistrySection({ chemistryData }) {
  const [activeTab, setActiveTab] = useState("bars"); // bars, scatter, table

  const teammates = chemistryData.teammates;
  const top10 = [...teammates]
    .sort((a, b) => b.shared_participations - a.shared_participations)
    .slice(0, 10);

  const renderBars = () => {
    const data = top10.map(t => ({
      name: `${t.name} #${t.jersey_number}`,
      volume: t.participations_per_game,
      efficiency: (t.shared_goals / t.shared_games), // Goals per game for foreground bar
      effPct: t.efficiency
    }));

    return (
      <div className="chemistry-viz-container">
        <h4 className="chart-subtitle">Yhteistyön Tehokkuus (MP & Maalit / peli)</h4>
        <ResponsiveContainer width="100%" height={top10.length * 40 + 40}>
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 5, right: 50, left: 40, bottom: 5 }}
            barGap={-20} // Overlay bars
          >
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
            <XAxis type="number" stroke="var(--muted-text)" fontSize={10} tickLine={false} />
            <YAxis 
              dataKey="name" 
              type="category" 
              stroke="var(--muted-text)" 
              fontSize={11} 
              tickLine={false}
              width={130}
            />
            <Tooltip 
              cursor={{ fill: "rgba(255,255,255,0.05)" }}
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const d = payload[0].payload;
                  return (
                    <div className="chemistry-tooltip">
                      <p className="tooltip-name">{d.name}</p>
                      <p className="tooltip-val">MP / peli: <span>{d.volume.toFixed(2)}</span></p>
                      <p className="tooltip-val">Maalit / peli: <span>{d.efficiency.toFixed(2)}</span></p>
                      <p className="tooltip-val">Tehokkuus: <span>{d.effPct}%</span></p>
                    </div>
                  );
                }
                return null;
              }}
            />
            {/* Background Bar: Volume */}
            <Bar dataKey="volume" fill="rgba(34, 197, 94, 0.2)" radius={[0, 4, 4, 0]} barSize={24} />
            {/* Foreground Bar: Efficiency */}
            <Bar dataKey="efficiency" fill="#22c55e" radius={[0, 4, 4, 0]} barSize={12}>
               <LabelList 
                 dataKey="effPct" 
                 position="right" 
                 formatter={(v) => `${v}%`} 
                 style={{ fill: 'var(--muted-text)', fontSize: '10px', fontWeight: 'bold' }} 
               />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const renderScatter = () => {
    const data = teammates.map(t => ({
      x: t.participations_per_game,
      y: t.efficiency,
      name: t.name,
      initials: t.name.split(' ').map(n => n[0]).join(''),
      jersey: `#${t.jersey_number}`
    }));

    return (
      <div className="chemistry-viz-container">
        <h4 className="chart-subtitle">Kemian Nelikenttä (Määrä vs. Tehokkuus)</h4>
        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis 
              type="number" 
              dataKey="x" 
              name="MP / peli" 
              stroke="var(--muted-text)" 
              fontSize={10}
              label={{ value: 'Yhteiset MP / peli', position: 'bottom', fill: 'var(--muted-text)', fontSize: 10 }}
            />
            <YAxis 
              type="number" 
              dataKey="y" 
              name="Tehokkuus %" 
              stroke="var(--muted-text)" 
              fontSize={10}
              label={{ value: 'Maalintekotehokkuus %', angle: -90, position: 'insideLeft', fill: 'var(--muted-text)', fontSize: 10 }}
            />
            <ZAxis type="number" range={[100, 100]} />
            <Tooltip 
              cursor={{ strokeDasharray: '3 3' }}
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const d = payload[0].payload;
                  return (
                    <div className="chemistry-tooltip">
                      <p className="tooltip-name">{d.name} {d.jersey}</p>
                      <p className="tooltip-val">MP / peli: <span>{d.x.toFixed(2)}</span></p>
                      <p className="tooltip-val">Tehokkuus: <span>{d.y.toFixed(1)}%</span></p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <ReferenceLine x={chemistryData.team_avg_volume} stroke="#ef4444" strokeDasharray="3 3" />
            <ReferenceLine y={chemistryData.team_avg_efficiency} stroke="#ef4444" strokeDasharray="3 3" />
            <Scatter name="Pelaajat" data={data} fill="var(--accent-color)">
               <LabelList dataKey="initials" position="top" style={{ fill: 'white', fontSize: '9px' }} />
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
        <div className="quadrant-labels">
           <span className="q-label top-right">Korkea määrä / Korkea teho</span>
           <span className="q-label top-left">Matala määrä / Korkea teho</span>
           <span className="q-label bottom-right">Korkea määrä / Matala teho</span>
           <span className="q-label bottom-left">Matala määrä / Matala teho</span>
        </div>
      </div>
    );
  };

  const renderTable = () => {
    const getEffClass = (eff) => {
      if (eff > 15) return "eff-high";
      if (eff >= 8) return "eff-mid";
      return "eff-low";
    };

    const maxMP = Math.max(...top10.map(t => t.participations_per_game), 0.1);

    return (
      <div className="chemistry-viz-container">
        <h4 className="chart-subtitle">Yhteistyön Tulostaulu (Top 10)</h4>
        <div className="chemistry-table-wrapper">
          <table className="chemistry-leaderboard">
            <thead>
              <tr>
                <th>Pelaaja</th>
                <th>Yhteiset pelit</th>
                <th>MP / Peli</th>
                <th>Tehokkuus %</th>
              </tr>
            </thead>
            <tbody>
              {top10.map((t, i) => (
                <tr key={i}>
                  <td className="player-cell">
                    <span className="jersey">{t.jersey_number}</span>
                    <span className="name">{t.name}</span>
                  </td>
                  <td>{t.shared_games}</td>
                  <td className="spark-cell">
                    <div className="spark-bar-bg">
                      <div 
                        className="spark-bar-fill" 
                        style={{ width: `${(t.participations_per_game / maxMP) * 100}%` }}
                      ></div>
                      <span className="spark-val">{t.participations_per_game.toFixed(2)}</span>
                    </div>
                  </td>
                  <td>
                    <span className={`eff-badge ${getEffClass(t.efficiency)}`}>
                      {t.efficiency.toFixed(1)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <section className="chemistry-section">
      <div className="section-header-row">
        <h3 className="section-title-small">Yhteistyö ja Kemia</h3>
        <div className="chemistry-tabs">
          <button 
            className={`tab-btn ${activeTab === "bars" ? "active" : ""}`}
            onClick={() => setActiveTab("bars")}
          >
            Tehokkuus
          </button>
          <button 
            className={`tab-btn ${activeTab === "scatter" ? "active" : ""}`}
            onClick={() => setActiveTab("scatter")}
          >
            Nelikenttä
          </button>
          <button 
            className={`tab-btn ${activeTab === "table" ? "active" : ""}`}
            onClick={() => setActiveTab("table")}
          >
            Tulostaulu
          </button>
        </div>
      </div>

      <div className="chemistry-content">
        {activeTab === "bars" && renderBars()}
        {activeTab === "scatter" && renderScatter()}
        {activeTab === "table" && renderTable()}
      </div>
    </section>
  );
}
