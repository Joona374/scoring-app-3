// src/pages/Analysis/Components/MapCanvas.jsx
import { useEffect, useRef } from "react";

export default function MapCanvas({ img, points, mode, heatRadius = 20 }) {
  const canvasRef = useRef(null);
  const imgRef = useRef(null);

  const getCategory = (label) => {
    if (!label) return "OTHER";
    if (label.startsWith("Maali")) return "GOAL";
    if (label.startsWith("MP")) return "CHANCE";
    if (label.startsWith("Laukaus")) return "SHOT";
    return "OTHER";
  };

  // crisp on HiDPI
  const resizeCanvasToDisplaySize = (canvas) => {
    const dpr = window.devicePixelRatio || 1;
    const { clientWidth, clientHeight } = canvas;
    const width = Math.round(clientWidth * dpr);
    const height = Math.round(clientHeight * dpr);
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width;
      canvas.height = height;
    }
    const ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.imageSmoothingEnabled = true;
  };

  // --- Scatter shapes ---
  const drawX = (ctx, x, y, size, color) => {
    // under-stroke for contrast
    ctx.lineWidth = 4;
    ctx.strokeStyle = "#0f0f0f";
    ctx.beginPath();
    ctx.moveTo(x - size, y - size);
    ctx.lineTo(x + size, y + size);
    ctx.moveTo(x + size, y - size);
    ctx.lineTo(x - size, y + size);
    ctx.stroke();

    ctx.lineWidth = 2.5;
    ctx.strokeStyle = color;
    ctx.beginPath();
    ctx.moveTo(x - size, y - size);
    ctx.lineTo(x + size, y + size);
    ctx.moveTo(x + size, y - size);
    ctx.lineTo(x - size, y + size);
    ctx.stroke();
  };

  const drawFilledCircle = (ctx, x, y, r, color) => {
    ctx.fillStyle = color;
    // thin outline for contrast
    ctx.lineWidth = 2;
    ctx.strokeStyle = "#0f0f0f";
    ctx.beginPath();
    ctx.arc(x, y, r + 1, 0, Math.PI * 2);
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  };

  const drawHollowCircle = (ctx, x, y, r, color) => {
    // dark under-stroke then color stroke
    ctx.lineWidth = 3;
    ctx.strokeStyle = "#0f0f0f";
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.stroke();

    ctx.lineWidth = 2;
    ctx.strokeStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.stroke();
  };

  const draw = () => {
    const image = imgRef.current;
    const canvas = canvasRef.current;
    if (!image || !canvas) return;
    const ctx = canvas.getContext("2d");

    resizeCanvasToDisplaySize(canvas);

    const cssW = image.clientWidth;
    const cssH = image.clientHeight;

    ctx.clearRect(0, 0, cssW, cssH);
    ctx.drawImage(image, 0, 0, cssW, cssH);

    if (!Array.isArray(points) || points.length === 0) return;

    if (mode === "heatmap") {
      points.forEach((p) => {
        const x = Math.round((p.x / 100) * cssW);
        const y = Math.round((p.y / 100) * cssH);
        const cat = getCategory(p.result);
        const r = p.is_goal ? heatRadius * 1.2 : heatRadius;
        const base = p.side === "FOR" ? "0,255,0" : "255,0,0";
        const alpha = cat === "GOAL" ? 0.28 : cat === "SHOT" ? 0.12 : 0.18;

        const grd = ctx.createRadialGradient(x, y, 0, x, y, r);
        grd.addColorStop(0, `rgba(${base},${alpha})`);
        grd.addColorStop(1, `rgba(${base},0)`);
        ctx.fillStyle = grd;
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fill();
      });
    } else {
      // Scatter: GOAL = large X, CHANCE = small filled circle, SHOT = hollow circle
      points.forEach((p) => {
        const x = Math.round((p.x / 100) * cssW);
        const y = Math.round((p.y / 100) * cssH);
        const cat = getCategory(p.result);
        const color = p.side === "FOR" ? "#22c55e" : "#ef4444";

        if (cat === "GOAL") {
          drawX(ctx, x, y, 9, color); // big X
        } else if (cat === "CHANCE") {
          drawFilledCircle(ctx, x, y, 5, color); // small filled dot
        } else if (cat === "SHOT") {
          drawHollowCircle(ctx, x, y, 6, color); // hollow circle
        } else {
          // fallback tiny dot
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(x, y, 3, 0, Math.PI * 2);
          ctx.fill();
        }
      });
    }
  };

  useEffect(() => {
    const ro = new ResizeObserver(draw);
    if (imgRef.current) ro.observe(imgRef.current);
    return () => ro.disconnect();
  }, []);

  useEffect(draw, [points, mode, heatRadius]);

  return (
    <div className="heat-wrap">
      <img ref={imgRef} src={img} alt="" className="heat-img" onLoad={draw} />
      <canvas ref={canvasRef} className="heat-canvas" />
    </div>
  );
}
