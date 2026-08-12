import { useRef, useEffect } from "react";
import maali from "../../../assets/maali.jpg";

const NET_ZONES = [
  { name: "Top-Left", row: 0, col: 0, x1: 0, y1: 0, x2: 35, y2: 35 },
  { name: "Top-Mid", row: 0, col: 1, x1: 35, y1: 0, x2: 65, y2: 35 },
  { name: "Top-Right", row: 0, col: 2, x1: 65, y1: 0, x2: 100, y2: 35 },
  { name: "Mid-Left", row: 1, col: 0, x1: 0, y1: 35, x2: 35, y2: 70 },
  { name: "Mid-Mid", row: 1, col: 1, x1: 35, y1: 35, x2: 65, y2: 70 },
  { name: "Mid-Right", row: 1, col: 2, x1: 65, y1: 35, x2: 100, y2: 70 },
  { name: "Bottom-Left", row: 2, col: 0, x1: 0, y1: 70, x2: 35, y2: 100 },
  { name: "Bottom-Mid", row: 2, col: 1, x1: 35, y1: 70, x2: 65, y2: 100 },
  { name: "Bottom-Right", row: 2, col: 2, x1: 65, y1: 70, x2: 100, y2: 100 },
];

export default function PlayerNetMap({ zoneStats, markers, mode = "goals_for", showMarkers = true, showZones = false }) {
  const imgRef = useRef(null);
  const canvasRef = useRef(null);

  const getDisplayValue = (zoneData) => {
    if (!zoneData) return { value: 0, label: "0" };
    const gf = zoneData.goals_for || 0;
    const cf = zoneData.chances_for || 0;

    switch (mode) {
      case "goals_for": return { value: gf, label: gf.toString() };
      case "chances_for": return { value: cf, label: cf.toString() };
      case "chances_for_no_goals": {
          const val = cf - gf;
          return { value: val, label: val.toString() };
      }
      case "efficiency_for": {
        const eff = cf > 0 ? (gf / cf) * 100 : 0;
        return { value: eff, label: eff.toFixed(1) + "%" };
      }
      default: return { value: 0, label: "0" };
    }
  };

  const allValues = Object.values(zoneStats || {}).map(zd => getDisplayValue(zd).value);
  const maxValue = Math.max(...allValues.map(Math.abs), 1);

  useEffect(() => {
    const img = imgRef.current;
    const canvas = canvasRef.current;
    if (!img || !canvas) return;

    const draw = () => {
      const ctx = canvas.getContext("2d");
      canvas.width = img.clientWidth;
      canvas.height = img.clientHeight;

      const percentToPx = (pct, dimension) => (pct / 100) * dimension;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // 1. Draw Zones
      if (showZones) {
        NET_ZONES.forEach((zone) => {
          const zoneData = zoneStats?.[zone.name];
          const { value, label } = getDisplayValue(zoneData);
          const intensity = Math.abs(value) / maxValue;

          const x = percentToPx(zone.x1, canvas.width);
          const y = percentToPx(zone.y1, canvas.height);
          const w = percentToPx(zone.x2 - zone.x1, canvas.width);
          const h = percentToPx(zone.y2 - zone.y1, canvas.height);

          if (value !== 0) {
            const alpha = 0.1 + intensity * 0.4;
            ctx.fillStyle = `rgba(34, 197, 94, ${alpha})`;
            ctx.fillRect(x, y, w, h);
          }

          ctx.strokeStyle = "rgba(255, 255, 255, 0.2)";
          ctx.lineWidth = 1;
          ctx.strokeRect(x, y, w, h);

          const cx = x + w / 2;
          const cy = y + h / 2;
          ctx.font = "bold 14px Arial";
          ctx.textAlign = "center";
          ctx.fillStyle = "rgba(255, 255, 255, 0.7)";
          ctx.fillText(label, cx, cy);
        });
      }

      // 2. Draw Markers
      if (showMarkers && markers) {
        markers.forEach(marker => {
          const mx = percentToPx(marker.x, canvas.width);
          const my = percentToPx(marker.y, canvas.height);
          const isGoal = marker.result === "Maali +";
          
          ctx.beginPath();
          if (isGoal) {
            ctx.arc(mx, my, 6, 0, Math.PI * 2);
            ctx.fillStyle = "#fbbf24";
            ctx.shadowBlur = 10;
            ctx.shadowColor = "#fbbf24";
          } else {
            ctx.arc(mx, my, 4, 0, Math.PI * 2);
            ctx.fillStyle = "#22c55e";
            ctx.shadowBlur = 0;
          }
          ctx.fill();
          ctx.strokeStyle = "white";
          ctx.lineWidth = 1.5;
          ctx.stroke();
          ctx.shadowBlur = 0;
        });
      }
    };

    if (img.complete) draw();
    else img.onload = draw;
    window.addEventListener("resize", draw);
    return () => window.removeEventListener("resize", draw);
  }, [zoneStats, mode, markers, showMarkers, showZones, maxValue]);

  return (
    <div className="zone-map-container">
      <img ref={imgRef} src={maali} alt="Maali" className="zone-map-img" />
      <canvas ref={canvasRef} className="zone-map-canvas" />
    </div>
  );
}
