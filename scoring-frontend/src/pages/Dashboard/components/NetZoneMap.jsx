import { useRef, useEffect } from "react";
import maali from "../../../assets/maali.jpg";

// Net zone definitions - 3x3 grid
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

export default function NetZoneMap({ zoneStats, mode = "goals_for", totals }) {
  const imgRef = useRef(null);
  const canvasRef = useRef(null);

  // Modes that should use green color (positive/offensive stats)
  const greenModes = [
    "goals_for", "chances_for", 
    "goals_for_pct", "chances_for_pct", 
    "efficiency_for"
  ];
  const isGreenMode = greenModes.includes(mode);

  // Calculate display value for a zone based on mode
  const getDisplayValue = (zoneData) => {
    if (!zoneData) return { value: 0, label: "0" };

    const gf = zoneData.goals_for || 0;
    const ga = zoneData.goals_against || 0;
    const cf = zoneData.chances_for || 0;
    const ca = zoneData.chances_against || 0;

    switch (mode) {
      // Raw counts
      case "goals_for": return { value: gf, label: gf.toString() };
      case "goals_against": return { value: ga, label: ga.toString() };
      case "chances_for": return { value: cf, label: cf.toString() };
      case "chances_against": return { value: ca, label: ca.toString() };
      
      // Percentages of total
      case "goals_for_pct": {
        const pct = totals.goals_for > 0 ? (gf / totals.goals_for) * 100 : 0;
        return { value: pct, label: pct.toFixed(1) + "%" };
      }
      case "goals_against_pct": {
        const pct = totals.goals_against > 0 ? (ga / totals.goals_against) * 100 : 0;
        return { value: pct, label: pct.toFixed(1) + "%" };
      }
      case "chances_for_pct": {
        const pct = totals.chances_for > 0 ? (cf / totals.chances_for) * 100 : 0;
        return { value: pct, label: pct.toFixed(1) + "%" };
      }
      case "chances_against_pct": {
        const pct = totals.chances_against > 0 ? (ca / totals.chances_against) * 100 : 0;
        return { value: pct, label: pct.toFixed(1) + "%" };
      }
      
      // Differentials and efficiency
      case "goals_diff": {
        const diff = gf - ga;
        return { value: diff, label: (diff > 0 ? "+" : "") + diff.toString(), isDiff: true };
      }
      case "chances_diff": {
        const diff = cf - ca;
        return { value: diff, label: (diff > 0 ? "+" : "") + diff.toString(), isDiff: true };
      }
      case "efficiency_for": {
        const eff = cf > 0 ? (gf / cf) * 100 : 0;
        return { value: eff, label: eff.toFixed(1) + "%" };
      }
      case "efficiency_against": {
        const eff = ca > 0 ? (ga / ca) * 100 : 0;
        return { value: eff, label: eff.toFixed(1) + "%" };
      }
      
      default: return { value: 0, label: "0" };
    }
  };

  // Find max absolute value for color scaling
  // Exclude values >= 100 (outliers like 1/1 = 100%) from max calculation
  const allValues = Object.values(zoneStats || {}).map(zd => getDisplayValue(zd).value);
  const filteredValues = allValues.filter(v => Math.abs(v) < 100);
  const maxValue = Math.max(...filteredValues.map(Math.abs), 1);

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

      // Draw each zone
      NET_ZONES.forEach((zone) => {
        const zoneData = zoneStats?.[zone.name];
        const { value, label, isDiff } = getDisplayValue(zoneData);
        
        // Cap intensity at 1 for outliers (100%+), otherwise scale normally
        const isOutlier = Math.abs(value) >= 100;
        const intensity = isOutlier ? 1 : Math.abs(value) / maxValue;

        const x = percentToPx(zone.x1, canvas.width);
        const y = percentToPx(zone.y1, canvas.height);
        const w = percentToPx(zone.x2 - zone.x1, canvas.width);
        const h = percentToPx(zone.y2 - zone.y1, canvas.height);

        // Fill with intensity-based color
        if (value !== 0) {
          const alpha = 0.2 + intensity * 0.5;
          // Determine color: green for "for" modes and positive diffs, red for "against" modes and negative diffs
          if (isDiff) {
            ctx.fillStyle = value > 0 
              ? `rgba(34, 197, 94, ${alpha})`  // green for positive diff
              : `rgba(185, 28, 28, ${alpha})`; // red for negative diff
          } else if (isGreenMode) {
            ctx.fillStyle = `rgba(34, 197, 94, ${alpha})`; // green for offensive stats
          } else {
            ctx.fillStyle = `rgba(185, 28, 28, ${alpha})`; // red for defensive stats
          }
          ctx.fillRect(x, y, w, h);
        }

        // Border
        ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
        ctx.lineWidth = 1;
        ctx.strokeRect(x, y, w, h);

        // Draw label
        const cx = x + w / 2;
        const cy = y + h / 2;

        ctx.font = "bold 16px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillStyle = "white";
        ctx.shadowColor = "black";
        ctx.shadowBlur = 3;
        ctx.fillText(label, cx, cy);
        ctx.shadowBlur = 0;
      });
    };

    if (img.complete) draw();
    else img.onload = draw;

    window.addEventListener("resize", draw);
    return () => window.removeEventListener("resize", draw);
  }, [zoneStats, mode, totals, maxValue]);

  return (
    <div className="zone-map-container">
      <img ref={imgRef} src={maali} alt="Maali" className="zone-map-img" />
      <canvas ref={canvasRef} className="zone-map-canvas" />
    </div>
  );
}
