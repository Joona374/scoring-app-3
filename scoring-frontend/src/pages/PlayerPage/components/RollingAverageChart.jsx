import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from "recharts";
import "./RollingAverageChart.css";

export default function RollingAverageChart({ 
  trendData, 
  teamAvgGoals, 
  teamAvgChances 
}) {
  // Format date for display
  const chartData = trendData.map(d => ({
    ...d,
    displayDate: new Date(d.date).toLocaleDateString("fi-FI", { day: "numeric", month: "numeric" }),
    fullDate: d.date,
  }));

  return (
    <section className="rolling-avg-section">
      <h3 className="section-title-small">Vire (5 pelin liukuva keskiarvo)</h3>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis 
              dataKey="displayDate" 
              stroke="var(--muted-text)" 
              fontSize={12}
              tickLine={false}
            />
            <YAxis 
              stroke="var(--muted-text)" 
              fontSize={12} 
              tickLine={false}
              axisLine={false}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: "#1e1d22", 
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "8px",
                fontSize: "12px"
              }}
              itemStyle={{ padding: "2px 0" }}
            />
            <Legend verticalAlign="top" height={36}/>
            
            {/* Team Baseline - Goals */}
            <ReferenceLine 
              y={teamAvgGoals} 
              stroke="#fbbf24" 
              strokeDasharray="3 3" 
              label={{ 
                value: "Joukkue M keskiarvo", 
                position: "insideBottomRight", 
                fill: "#fbbf24", 
                fontSize: 10 
              }} 
            />
            
            {/* Team Baseline - Chances */}
            <ReferenceLine 
              y={teamAvgChances} 
              stroke="#22c55e" 
              strokeDasharray="3 3" 
              label={{ 
                value: "Joukkue MP keskiarvo", 
                position: "insideTopRight", 
                fill: "#22c55e", 
                fontSize: 10 
              }} 
            />

            <Line
              type="monotone"
              dataKey="rolling_chances"
              name="Maalipaikat (liukuva)"
              stroke="#22c55e"
              strokeWidth={3}
              dot={{ r: 4, fill: "#22c55e", strokeWidth: 2, stroke: "#1e1d22" }}
              activeDot={{ r: 6, strokeWidth: 0 }}
            />
            <Line
              type="monotone"
              dataKey="rolling_goals"
              name="Maalit (liukuva)"
              stroke="#fbbf24"
              strokeWidth={3}
              dot={{ r: 4, fill: "#fbbf24", strokeWidth: 2, stroke: "#1e1d22" }}
              activeDot={{ r: 6, strokeWidth: 0 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
