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
  const data = synergyData.points.map(p => ({
    name: `${p.teammate_name} #${p.jersey_number}`,
    value: p.net_mp_per_game,
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const val = payload[0].value;
      return (
        <div className="synergy-tooltip">
          <p className="tooltip-teammate">{payload[0].payload.name}</p>
          <p className={`tooltip-value ${val >= 0 ? "positive" : "negative"}`}>
            Net MP/peli: <span>{val > 0 ? `+${val}` : val}</span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <section className="synergy-chart-section">
      <h3 className="section-title-small">Kentällä yhdessä (On-Ice +/-)</h3>
      <div className="synergy-container">
        <ResponsiveContainer width="100%" height={Math.max(data.length * 35, 200)}>
          <BarChart
            data={data}
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
              fontSize={10} 
              tickLine={false}
              width={120}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.05)" }} />
            <ReferenceLine x={0} stroke="rgba(255,255,255,0.2)" />
            <Bar dataKey="value" radius={[0, 4, 4, 0]}>
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.value >= 0 ? "#22c55e" : "#ef4444"} 
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
