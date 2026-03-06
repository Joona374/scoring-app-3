import { useState, useMemo } from "react";
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
  ReferenceLine,
  Cell
} from "recharts";
import "./ChemistrySection.css";
import InfoTooltip from "./InfoTooltip";

export default function ChemistrySection({ chemistryData }) {
  const [activeTab, setActiveTab] = useState("bars"); // bars, scatter, table
  const [posFilter, setPosFilter] = useState("ALL"); // ALL, FORWARD, DEFENDER

  const allTeammates = chemistryData.teammates;
  
  const filteredTeammates = useMemo(() => {
    if (posFilter === "ALL") return allTeammates;
    return allTeammates.filter(t => t.position === posFilter);
  }, [allTeammates, posFilter]);

  const top10 = useMemo(() => [...filteredTeammates]
    .sort((a, b) => b.shared_participations - a.shared_participations)
    .slice(0, 10), [filteredTeammates]);

  const getTabInfo = () => {
    switch (activeTab) {
      case "bars": return "Vertailee kuinka monta maalipaikkaa pelaaja luo yhdessä kunkin joukkuekaverin kanssa (osallisuudet per peli) ja kuinka suuri osa näistä johtaa maaliin.";
      case "scatter": return "Sijoittaa joukkuekaverit nelikenttään yhteisten maalipaikkojen määrän (X-akseli) ja niiden viimeistelytehokkuuden (Y-akseli) perusteella. Akseleiden risteyskohta on joukkueen keskiarvo.";
      case "table": return "Yhteenveto parhaista tutkapareista. MP / Peli on visualisoitu palkeilla ja tehokkuus värikoodeilla (Vihreä > 15%, Keltainen 8-15%, Punainen < 8%).";
      default: return "";
    }
  };

  const renderBars = () => {
    const data = top10.map(t => ({
      name: `${t.name} #${t.jersey_number}`,
      volume: t.participations_per_game,
      efficiency: (t.shared_goals / t.shared_games),
      effPct: t.efficiency
    }));

    return (
      <div className="chemistry-viz-container">
        <h4 className="chart-subtitle">Yhteistyön Tehokkuus (MP & Maalit / peli)</h4>
        <ResponsiveContainer width="100%" height={top10.length * 40 + 40}>
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 50, left: 40, bottom: 5 }} barGap={-20}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
            <XAxis type="number" stroke="var(--muted-text)" fontSize={10} tickLine={false} />
            <YAxis dataKey="name" type="category" stroke="var(--muted-text)" fontSize={11} tickLine={false} width={130} />
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
            <Bar dataKey="volume" fill="rgba(34, 197, 94, 0.2)" radius={[0, 4, 4, 0]} barSize={24} />
            <Bar dataKey="efficiency" fill="#22c55e" radius={[0, 4, 4, 0]} barSize={12}>
               <LabelList dataKey="effPct" position="right" formatter={(v) => `${v}%`} style={{ fill: 'var(--muted-text)', fontSize: '10px', fontWeight: 'bold' }} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const renderScatter = () => {
    const avgVolume = chemistryData.team_avg_volume;
    const avgEff = chemistryData.team_avg_efficiency;
    let maxX = 0;
    const data = filteredTeammates.map(t => {
      if (t.participations_per_game > maxX) maxX = t.participations_per_game;
      const cappedY = Math.min(t.efficiency, 50);
      let color = "#94a3b8";
      if (t.participations_per_game >= avgVolume && t.efficiency >= avgEff) color = "#22c55e";
      else if (t.participations_per_game < avgVolume && t.efficiency >= avgEff) color = "#3b82f6";
      else if (t.participations_per_game >= avgVolume && t.efficiency < avgEff) color = "#fbbf24";
      else color = "#ef4444";
      return { x: t.participations_per_game, y: cappedY, actualY: t.efficiency, name: t.name, initials: t.name.split(' ').map(n => n[0]).join(''), jersey: `#${t.jersey_number}`, fill: color };
    });

    return (
      <div className="chemistry-viz-container">
        <h4 className="chart-subtitle">Kemian Nelikenttä (Määrä vs. Tehokkuus)</h4>
        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart margin={{ top: 20, right: 30, bottom: 30, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis type="number" dataKey="x" name="MP / peli" stroke="var(--muted-text)" fontSize={11} domain={[0, maxX || 1]} tickCount={maxX > 2 ? 6 : 3} label={{ value: 'Yhteiset MP / peli', position: 'bottom', fill: 'var(--muted-text)', fontSize: 12, offset: 10 }} />
            <YAxis type="number" dataKey="y" name="Tehokkuus %" stroke="var(--muted-text)" fontSize={11} domain={[0, 50]} label={{ value: 'Maalintekotehokkuus %', angle: -90, position: 'insideLeft', fill: 'var(--muted-text)', fontSize: 12, offset: -5 }} />
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
                      <p className="tooltip-val">Tehokkuus: <span>{d.actualY.toFixed(1)}%</span></p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <ReferenceLine x={avgVolume} stroke="rgba(255,255,255,0.4)" strokeDasharray="3 3" label={{ value: 'Joukkueen KA', position: 'top', fill: 'var(--muted-text)', fontSize: 10 }} />
            <ReferenceLine y={avgEff} stroke="rgba(255,255,255,0.4)" strokeDasharray="3 3" label={{ value: 'KA Tehokkuus', position: 'right', fill: 'var(--muted-text)', fontSize: 10 }} />
            <Scatter name="Pelaajat" data={data}>
               {data.map((entry, index) => ( <Cell key={`cell-${index}`} fill={entry.fill} /> ))}
               <LabelList dataKey="initials" position="top" style={{ fill: 'white', fontSize: '9px', fontWeight: 'bold' }} />
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
        <div className="quadrant-grid-legend">
           <div className="quadrant-legend-cell top-left"><span className="q-dot blue"></span> Matala määrä / Korkea teho</div>
           <div className="quadrant-legend-cell top-right">Korkea määrä / Korkea teho <span className="q-dot green"></span></div>
           <div className="quadrant-legend-cell bottom-left"><span className="q-dot red"></span> Matala määrä / Matala teho</div>
           <div className="quadrant-legend-cell bottom-right">Korkea määrä / Matala teho <span className="q-dot yellow"></span></div>
        </div>
      </div>
    );
  };

  const renderTable = () => {
    const getEffClass = (eff) => { if (eff > 15) return "eff-high"; if (eff >= 8) return "eff-mid"; return "eff-low"; };
    const maxMP = Math.max(...top10.map(t => t.participations_per_game), 0.1);
    return (
      <div className="chemistry-viz-container">
        <h4 className="chart-subtitle">Yhteistyön Tulostaulu (Top {top10.length})</h4>
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
                  <td className="player-cell"> <span className="jersey">{t.jersey_number}</span> <span className="name">{t.name}</span> </td>
                  <td>{t.shared_games}</td>
                  <td className="spark-cell"> <div className="spark-bar-bg"> <div className="spark-bar-fill" style={{ width: `${(t.participations_per_game / maxMP) * 100}%` }}></div> <span className="spark-val">{t.participations_per_game.toFixed(2)}</span> </div> </td>
                  <td> <span className={`eff-badge ${getEffClass(t.efficiency)}`}> {t.efficiency.toFixed(1)}% </span> </td>
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
      <div className="section-header-row unified-row info-row">
        <div className="header-title-with-info">
          <h3 className="section-title-small">Yhteistyö ja Kemia</h3>
          <InfoTooltip text={getTabInfo()} />
        </div>
        
        <div className="header-tabs-container">
          <div className="filter-tabs pos-filters">
            <button className={`filter-tab ${posFilter === "ALL" ? "active" : ""}`} onClick={() => setPosFilter("ALL")}> Kaikki </button>
            <button className={`filter-tab ${posFilter === "FORWARD" ? "active" : ""}`} onClick={() => setPosFilter("FORWARD")}> Hyökkääjät </button>
            <button className={`filter-tab ${posFilter === "DEFENDER" ? "active" : ""}`} onClick={() => setPosFilter("DEFENDER")}> Puolustajat </button>
          </div>
          <div className="chemistry-tabs viz-filters">
            <button className={`tab-btn ${activeTab === "bars" ? "active" : ""}`} onClick={() => setActiveTab("bars")}> Tehokkuus </button>
            <button className={`tab-btn ${activeTab === "scatter" ? "active" : ""}`} onClick={() => setActiveTab("scatter")}> Nelikenttä </button>
            <button className={`tab-btn ${activeTab === "table" ? "active" : ""}`} onClick={() => setActiveTab("table")}> Tulostaulu </button>
          </div>
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
