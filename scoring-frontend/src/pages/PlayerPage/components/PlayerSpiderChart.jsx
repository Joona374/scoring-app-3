import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip
} from "recharts";
import "./PlayerSpiderChart.css";

export default function PlayerSpiderChart({ spiderData, playerName }) {
  // Normalize data for visualization while keeping original values for tooltips
  // We want to scale each KPI relative to the max of {player_value, team_avg} 
  // so the chart looks balanced even with different units.
  const chartData = spiderData.kpis.map(kpi => {
    const maxValue = Math.max(kpi.player_value, kpi.team_avg, 0.1);
    return {
      subject: kpi.label,
      player: (kpi.player_value / maxValue) * 100,
      team: (kpi.team_avg / maxValue) * 100,
      fullPlayer: kpi.player_value,
      fullTeam: kpi.team_avg,
    };
  });

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="spider-tooltip">
          <p className="tooltip-label">{data.subject}</p>
          <p className="tooltip-value player">
            {playerName}: <span>{data.fullPlayer}</span>
          </p>
          <p className="tooltip-value team">
            Joukkueen ka: <span>{data.fullTeam}</span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <section className="spider-chart-section">
      <h3 className="section-title-small">Suorituskyky vs. Joukkue</h3>
      <div className="spider-container">
        <ResponsiveContainer width="100%" height={320}>
          <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
            <PolarGrid stroke="rgba(255,255,255,0.1)" />
            <PolarAngleAxis 
              dataKey="subject" 
              tick={{ fill: "var(--muted-text)", fontSize: 10, fontWeight: 600 }} 
            />
            <PolarRadiusAxis 
              angle={30} 
              domain={[0, 100]} 
              tick={false} 
              axisLine={false} 
            />
            
            <Radar
              name="Joukkueen keskiarvo"
              dataKey="team"
              stroke="rgba(255, 255, 255, 0.3)"
              fill="rgba(255, 255, 255, 0.1)"
              fillOpacity={0.5}
            />
            <Radar
              name={playerName}
              dataKey="player"
              stroke="var(--accent-color)"
              fill="var(--accent-color)"
              fillOpacity={0.4}
            />
            
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              verticalAlign="bottom" 
              height={36}
              wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
