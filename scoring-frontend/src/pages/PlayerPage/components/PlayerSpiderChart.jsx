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
import InfoTooltip from "./InfoTooltip";

export default function PlayerSpiderChart({ spiderData, playerName }) {
  // Normalize data so team average is always at 50% mark
  const chartData = spiderData.kpis.map(kpi => {
    const playerVal = kpi.player_value;
    const avgVal = kpi.team_avg;
    
    let normalizedPlayer = 50;
    if (avgVal > 0) {
      if (playerVal >= avgVal) {
        const maxVal = Math.max(avgVal * 2, playerVal * 1.2, 0.1);
        normalizedPlayer = 50 + ((playerVal - avgVal) / (maxVal - avgVal)) * 50;
      } else {
        normalizedPlayer = (playerVal / avgVal) * 50;
      }
    } else {
      normalizedPlayer = playerVal > 0 ? 100 : 0;
    }

    return {
      subject: kpi.label,
      player: normalizedPlayer,
      team: 50,
      fullPlayer: playerVal,
      fullTeam: avgVal,
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

  const getKpiExplanation = (label) => {
    switch (label) {
      case "Maalit / peli": return "Pelaajan tekemät maalit suhteutettuna ottelumäärään. Kuvaa puhdasta viimeistelytehoa.";
      case "Osallisuudet / peli": return "Kuinka usein pelaaja on mukana luomassa maalipaikkaa (laukaisija tai osallistuja). Kuvaa hyökkäyspään aktiivisuutta.";
      case "5v5 Corsi %": return "Omien ja vastustajan maalipaikkojen suhde pelaajan ollessa jäällä 5v5-pelissä. Yli 50% tarkoittaa, että joukkue luo enemmän paikkoja kuin vastustaja pelaajan ollessa jäällä.";
      case "YV Tehokkuus %": return "Maalien osuus kaikista ylivoimalla luoduista maalipaikoista pelaajan ollessa jäällä.";
      case "AV Työkuorma": return "Kuinka monta vastustajan maalipaikkaa pelaaja kohtaa keskimäärin yhdessä alivoimaottelussa. Mitä pienempi luku, sitä vähemmän vaaraa omaan päähän syntyy.";
      default: return "";
    }
  };

  return (
    <section className="spider-chart-section">
      <div className="section-header-row info-row">
        <h3 className="section-title-small">Suorituskyky vs. Joukkue</h3>
        <InfoTooltip text="Pelaajan vertailu joukkueen muihin kenttäpelaajiin. Keskipisteen (50%) kehä kuvaa joukkueen keskiarvoa kussakin kategoriassa." />
      </div>
      
      <div className="spider-container">
        {/* Simple legend/guide for the labels since we can't easily put HTML inside Radar SVG ticks */}
        <div className="spider-labels-guide">
           {spiderData.kpis.map((kpi, i) => (
             <div key={i} className="label-guide-item">
                <span className="label-text">{kpi.label}</span>
                <InfoTooltip text={getKpiExplanation(kpi.label)} />
             </div>
           ))}
        </div>

        <ResponsiveContainer width="100%" height={380}>
          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
            <PolarGrid stroke="rgba(255,255,255,0.1)" />
            <PolarAngleAxis 
              dataKey="subject" 
              tick={{ fill: "var(--muted-text)", fontSize: 10, fontWeight: 700 }}
            />
            <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
            <Radar name="Joukkueen keskiarvo" dataKey="team" stroke="rgba(255, 255, 255, 0.4)" fill="rgba(255, 255, 255, 0.1)" fillOpacity={0.5} strokeDasharray="4 4" />
            <Radar name={playerName} dataKey="player" stroke="var(--accent-color)" fill="var(--accent-color)" fillOpacity={0.4} />
            <Tooltip content={<CustomTooltip />} />
            <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: '12px', paddingTop: '15px' }} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
