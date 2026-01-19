import { useRef, useEffect } from "react";
import kaukalo from "../../../assets/kaukalo.png";

// Zone definitions matching the tagging component
const ICE_ZONES = [
  {
    name: "BLUELINE",
    points: [
      [0, 0],
      [100, 0],
      [100, 12],
      [0, 12],
    ],
  },
  {
    name: "HIGH_SLOT",
    points: [
      [0, 11],
      [100, 11],
      [100, 23],
      [0, 23],
    ],
  },
  {
    name: "MISC",
    points: [
      [0, 79],
      [100, 79],
      [100, 100],
      [0, 100],
    ],
  },
  {
    name: "OUTSIDE_CLOSE",
    label: "OC-L",
    points: [
      [50, 79],
      [25, 79],
      [25, 60],
    ],
  },
  {
    name: "OUTSIDE_FAR",
    label: "OF-L",
    points: [
      [0, 40],
      [25, 60],
      [25, 79],
      [0, 79],
    ],
  },
  {
    name: "ZONE_4",
    label: "Z4-L",
    points: [
      [0, 23],
      [25, 23],
      [25, 60],
      [0, 40],
    ],
  },
  {
    name: "OUTSIDE_CLOSE",
    label: "OC-R",
    points: [
      [50, 79],
      [75, 79],
      [75, 60],
    ],
  },
  {
    name: "OUTSIDE_FAR",
    label: "OF-R",
    points: [
      [100, 40],
      [75, 60],
      [75, 79],
      [100, 79],
    ],
  },
  {
    name: "ZONE_4",
    label: "Z4-R",
    points: [
      [100, 23],
      [75, 23],
      [75, 60],
      [100, 40],
    ],
  },
  {
    name: "ZONE_2_SIDE",
    label: "Z2-L",
    points: [
      [25, 23],
      [40, 23],
      [40, 50],
      [25, 60],
    ],
  },
  {
    name: "ZONE_2_MIDDLE",
    points: [
      [40, 23],
      [60, 23],
      [60, 50],
      [40, 50],
    ],
  },
  {
    name: "ZONE_2_SIDE",
    label: "Z2-R",
    points: [
      [75, 23],
      [60, 23],
      [60, 50],
      [75, 60],
    ],
  },
  {
    name: "ZONE_1",
    points: [
      [50, 79],
      [25, 60],
      [40, 50],
      [60, 50],
      [75, 60],
    ],
  },
];



export default function IceZoneMap({ zoneStats, mode = "goals_for", totals }) {
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

      const percentToPx = ([x, y]) => [
        (x / 100) * canvas.width,
        (y / 100) * canvas.height,
      ];

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw each zone
      ICE_ZONES.forEach((zone) => {
        const zoneData = zoneStats?.[zone.name];
        const { value, label, isDiff } = getDisplayValue(zoneData);
        
        // Cap intensity at 1 for outliers (100%+), otherwise scale normally
        const isOutlier = Math.abs(value) >= 100;
        const intensity = isOutlier ? 1 : Math.abs(value) / maxValue;

        ctx.beginPath();
        zone.points.forEach(([x, y], idx) => {
          const [px, py] = percentToPx([x, y]);
          if (idx === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        });
        ctx.closePath();

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
          ctx.fill();
        }

        // Light border
        ctx.strokeStyle = "rgba(255, 255, 255, 0.2)";
        ctx.lineWidth = 1;
        ctx.stroke();
      });

      // Draw labels
      ctx.font = "bold 14px Arial";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      ICE_ZONES.forEach((zone) => {
        const zoneData = zoneStats?.[zone.name];
        const { label } = getDisplayValue(zoneData);
        
        // Calculate centroid
        const centroid = zone.points.reduce(
          (acc, [x, y]) => [acc[0] + x, acc[1] + y],
          [0, 0]
        );
        centroid[0] /= zone.points.length;
        centroid[1] /= zone.points.length;

        const [cx, cy] = percentToPx(centroid);

        // Draw label
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
      <img ref={imgRef} src={kaukalo} alt="Kaukalo" className="zone-map-img" />
      <canvas ref={canvasRef} className="zone-map-canvas" />
    </div>
  );
}
