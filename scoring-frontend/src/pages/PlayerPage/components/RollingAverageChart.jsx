import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import "./RollingAverageChart.css";

export default function RollingAverageChart({
  trendData,
  playerName,
  playerPosition,
}) {
  // Format data for display
  const chartData = trendData.map((d) => ({
    ...d,
    displayDate: new Date(d.date).toLocaleDateString("fi-FI", {
      day: "numeric",
      month: "numeric",
    }),
    fullDate: d.date,
  }));

  const positionLabel =
    playerPosition === "FORWARD" ? "Hyökkääjät" : "Puolustajat";

  const renderChart = (
    dataKey,
    teamDataKey,
    title,
    color,
    teamColor,
    label,
  ) => (
    <div className="chart-wrapper">
      <h4 className="chart-subtitle">{title}</h4>
      <ResponsiveContainer width="100%" height={170}>
        <LineChart
          data={chartData}
          margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
          style={{ outline: "none" }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="rgba(255,255,255,0.05)"
            vertical={false}
          />
          <XAxis
            dataKey="displayDate"
            stroke="var(--muted-text)"
            fontSize={10}
            tickLine={false}
            axisLine={false}
            padding={{ left: 10, right: 10 }}
          />
          <YAxis
            stroke="var(--muted-text)"
            fontSize={10}
            tickLine={false}
            axisLine={false}
            domain={[0, "auto"]}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1e1d22",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "8px",
              fontSize: "11px",
            }}
          />
          <Legend
            verticalAlign="top"
            align="right"
            height={24}
            iconSize={10}
            wrapperStyle={{
              marginRight: "-10px",
              fontSize: "10px",
              marginTop: "-10px",
            }}
          />

          <Line
            type="monotone"
            dataKey={teamDataKey}
            name={`Keskiarvo ${positionLabel}`}
            stroke={teamColor}
            strokeWidth={2}
            strokeDasharray="4 4"
            dot={false}
            activeDot={false}
            isAnimationActive={true}
          />
          <Line
            type="monotone"
            dataKey={dataKey}
            name={playerName}
            stroke={color}
            strokeWidth={3}
            dot={{ r: 3, fill: color, strokeWidth: 0 }}
            activeDot={{ r: 5, strokeWidth: 0 }}
            isAnimationActive={true}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );

  return (
    <section className="rolling-avg-section">
      <h3 className="section-title-small">Vire (5 pelin liukuva keskiarvo)</h3>
      <div className="charts-vertical-stack">
        {renderChart(
          "rolling_goals",
          "team_rolling_goals",
          "MAALIT",
          "#fbbf24",
          "#ef4444",
          "M",
        )}
        {renderChart(
          "rolling_chances",
          "team_rolling_chances",
          "MAALIPAIKAT",
          "#22c55e",
          "#3b82f6",
          "MP",
        )}
      </div>
    </section>
  );
}
