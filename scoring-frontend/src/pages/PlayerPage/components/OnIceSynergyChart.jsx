import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine
} from "recharts";
import "./OnIceSynergyChart.css";

export default function OnIceSynergyChart({ synergyData }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const fullData = synergyData.points.map(p => ({
    name: `${p.teammate_name} #${p.jersey_number}`,
    value: p.net_mp_per_game,
    sharedGames: p.shared_games
  }));

  // Logic for collapsed view (Top 5 and Bottom 5)
  const getDisplayData = () => {
    if (isExpanded || fullData.length <= 10) return fullData;
    
    const top5 = fullData.slice(0, 5);
    const bottom5 = fullData.slice(-5);
    
    // Add a placeholder for the middle
    return [...top5, { name: "...", value: 0, isPlaceholder: true }, ...bottom5];
  };

  const displayData = getDisplayData();

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      if (data.isPlaceholder) return null;
      
      const val = payload[0].value;
      return (
        <div className="synergy-tooltip">
          <p className="tooltip-teammate">{data.name}</p>
          <p className={`tooltip-value ${val >= 0 ? "positive" : "negative"}`}>
            Net MP/peli: <span>{val > 0 ? `+${val}` : val}</span>
          </p>
          <p className="tooltip-games">Yhteiset pelit: {data.sharedGames}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <section className="synergy-chart-section">
      <div className="section-header-row">
        <h3 className="section-title-small">Kentällä yhdessä (On-Ice +/-)</h3>
        {fullData.length > 10 && (
          <button 
            className="expand-btn" 
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? "Näytä vähemmän" : "Näytä kaikki"}
          </button>
        )}
      </div>
      
      <div className={`synergy-container ${isExpanded ? "expanded" : "collapsed"}`}>
        <ResponsiveContainer width="100%" height={displayData.length * 35}>
          <BarChart
            data={displayData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
            style={{ outline: 'none' }}
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
              tick={(props) => {
                const { x, y, payload } = props;
                if (payload.value === "...") {
                  return (
                    <text x={x} y={y} dy={4} fill="var(--muted-text)" fontSize={16} fontWeight="bold" textAnchor="end">
                      ...
                    </text>
                  );
                }
                return (
                  <text x={x} y={y} dy={4} fill="var(--muted-text)" fontSize={11} textAnchor="end">
                    {payload.value}
                  </text>
                );
              }}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.05)" }} />
            <ReferenceLine x={0} stroke="rgba(255,255,255,0.2)" />
            <Bar dataKey="value" radius={[0, 4, 4, 0]} animationDuration={500}>
              {displayData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.isPlaceholder ? "transparent" : (entry.value >= 0 ? "#22c55e" : "#ef4444")} 
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
