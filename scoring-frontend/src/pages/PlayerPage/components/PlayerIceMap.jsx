import { useRef, useEffect } from "react";
import kaukalo from "../../../assets/kaukalo.png";

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
    name: "OUTSIDE_CLOSE_LEFT",
    label: "OC-L",
    points: [
      [50, 79],
      [25, 79],
      [25, 60],
    ],
  },
  {
    name: "OUTSIDE_FAR_LEFT",
    label: "OF-L",
    points: [
      [0, 40],
      [25, 60],
      [25, 79],
      [0, 79],
    ],
  },
  {
    name: "ZONE_4_LEFT",
    label: "Z4-L",
    points: [
      [0, 23],
      [25, 23],
      [25, 60],
      [0, 40],
    ],
  },
  {
    name: "OUTSIDE_CLOSE_RIGHT",
    label: "OC-R",
    points: [
      [50, 79],
      [75, 79],
      [75, 60],
    ],
  },
  {
    name: "OUTSIDE_FAR_RIGHT",
    label: "OF-R",
    points: [
      [100, 40],
      [75, 60],
      [75, 79],
      [100, 79],
    ],
  },
  {
    name: "ZONE_4_RIGHT",
    label: "Z4-R",
    points: [
      [100, 23],
      [75, 23],
      [75, 60],
      [100, 40],
    ],
  },
  {
    name: "ZONE_2_SIDE_LEFT",
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
    name: "ZONE_2_SIDE_RIGHT",
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

export default function PlayerIceMap({ zoneStats, markers, mode = "goals_for", showMarkers = true, showZones = false }) {
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

      const percentToPx = ([x, y]) => [
        (x / 100) * canvas.width,
        (y / 100) * canvas.height,
      ];

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // 1. Draw Zones
      if (showZones) {
        ICE_ZONES.forEach((zone) => {
          const zoneData = zoneStats?.[zone.name];
          const { value, label } = getDisplayValue(zoneData);
          const intensity = Math.abs(value) / maxValue;

          ctx.beginPath();
          zone.points.forEach(([x, y], idx) => {
            const [px, py] = percentToPx([x, y]);
            if (idx === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
          });
          ctx.closePath();

          if (value !== 0) {
            const alpha = 0.1 + intensity * 0.4;
            ctx.fillStyle = `rgba(34, 197, 94, ${alpha})`;
            ctx.fill();
          }

          ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
          ctx.lineWidth = 1;
          ctx.stroke();

          // Label
          const centroid = zone.points.reduce((acc, [x, y]) => [acc[0] + x, acc[1] + y], [0, 0]);
          const [cx, cy] = percentToPx([centroid[0] / zone.points.length, centroid[1] / zone.points.length]);
          ctx.font = "bold 12px Arial";
          ctx.textAlign = "center";
          ctx.fillStyle = "rgba(255, 255, 255, 0.7)";
          ctx.fillText(label, cx, cy);
        });
      }

      // 2. Draw Markers
      if (showMarkers && markers) {
        markers.forEach(marker => {
          const [mx, my] = percentToPx([marker.x, marker.y]);
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
      <img ref={imgRef} src={kaukalo} alt="Kaukalo" className="zone-map-img" />
      <canvas ref={canvasRef} className="zone-map-canvas" />
    </div>
  );
}
