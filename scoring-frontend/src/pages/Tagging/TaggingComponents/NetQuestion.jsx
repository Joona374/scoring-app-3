import { useContext, useRef, useState, useEffect } from "react";
import { TaggingContext } from "../../../context/TaggingContext";
import maali from "../../../assets/maali.jpg";
import "../Styles/ShotLocationQuestion.css";

export default function NetQuestion() {
  const { currentTag, questionObjects, currentQuestionId, advanceQuestion } =
    useContext(TaggingContext);

  const imgRef = useRef(null);
  const canvasRef = useRef(null);
  const [hovering, setHovering] = useState(null);
  const [zoneHovering, setZoneHovering] = useState(null);

  // Get the current question using the currentQuestionId
  const currentQuestion = questionObjects.find(
    (q) => q.id === currentQuestionId
  );

  const shotZones = [
    {
      name: "Miss-Left",
      points: [
        [0, 0],
        [6, 0],
        [6, 100],
        [0, 100],
      ],
    },
    {
      name: "Miss-Right",
      points: [
        [94, 0],
        [100, 0],
        [100, 100],
        [94, 100],
      ],
    },

    {
      name: "Top-Left",
      points: [
        [6, 0],
        [35, 0],
        [35, 35],
        [6, 35],
      ],
    },

    {
      name: "Top-Mid",
      points: [
        [35, 0],
        [65, 0],
        [65, 35],
        [35, 35],
      ],
    },

    {
      name: "Top-Left",
      points: [
        [94, 0],
        [65, 0],
        [65, 35],
        [94, 35],
      ],
    },

    {
      name: "Mid-Left",
      points: [
        [6, 35],
        [35, 35],
        [35, 70],
        [6, 70],
      ],
    },

    {
      name: "Mid-Mid",
      points: [
        [35, 35],
        [65, 35],
        [65, 70],
        [35, 70],
      ],
    },

    {
      name: "Mid-Left",
      points: [
        [94, 35],
        [65, 35],
        [65, 70],
        [94, 70],
      ],
    },
    {
      name: "Bottom-Left",
      points: [
        [6, 70],
        [35, 70],
        [35, 100],
        [6, 100],
      ],
    },

    {
      name: "Bottom-Mid",
      points: [
        [35, 70],
        [65, 70],
        [65, 100],
        [35, 100],
      ],
    },

    {
      name: "Bottom-Left",
      points: [
        [94, 70],
        [65, 70],
        [65, 100],
        [94, 100],
      ],
    },
  ];

  function pointInZone([x, y], zone) {
    let inside = false;
    for (let i = 0, j = zone.length - 1; i < zone.length; j = i++) {
      const [xi, yi] = zone[i];
      const [xj, yj] = zone[j];

      const intersect =
        yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi;

      if (intersect) inside = !inside;
    }
    return inside;
  }

  const drawZone = (hoverIndex = null) => {
    const img = imgRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    canvas.width = img.clientWidth;
    canvas.height = img.clientHeight;

    const percentToPx = ([x, y]) => [
      (x / 100) * canvas.width,
      (y / 100) * canvas.height,
    ];

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    shotZones.forEach((zone, index) => {
      ctx.beginPath();
      zone.points.forEach(([x, y], idx) => {
        const [px, py] = percentToPx([x, y]);
        if (idx === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      });
      ctx.closePath();

      if (index === hoverIndex) {
        ctx.fillStyle = "rgba(0, 255, 0, 0.1)";

        ctx.fill();
        ctx.strokeStyle = "rgba(0, 255, 0, 0.5)";
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    });
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    const img = imgRef.current;
    const ctx = canvas.getContext("2d");

    const resize = () => drawZone(hovering);
    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      const mouseX = ((e.clientX - rect.left) / rect.width) * 100;
      const mouseY = ((e.clientY - rect.top) / rect.height) * 100;

      let hoveredIndex = null;

      for (let i = 0; i < shotZones.length; i++) {
        if (pointInZone([mouseX, mouseY], shotZones[i].points)) {
          hoveredIndex = i;
          break;
        }
      }

      setHovering((prev) => {
        if (prev !== hoveredIndex) {
          drawZone(hoveredIndex); // Only redraw if changed
          if (hoveredIndex !== null) {
            setZoneHovering(shotZones[hoveredIndex].name);
          } else {
            setZoneHovering(null);
          }
        }
        return hoveredIndex;
      });
    };

    // Resize + hover listeners
    window.addEventListener("resize", resize);
    canvas.addEventListener("mousemove", handleMouseMove);

    if (img.complete) drawZone();
    else img.onload = () => drawZone();

    return () => {
      window.removeEventListener("resize", resize);
      canvas.removeEventListener("mousemove", handleMouseMove);
    };
  }, []);

  const handleCanvasClick = (event) => {
    const img = event.target;

    const x = event.nativeEvent.offsetX;
    const imageWidth = img.offsetWidth;
    const percentageX = Math.round((x / imageWidth) * 100);

    const y = event.nativeEvent.offsetY;
    const imageHeight = img.offsetHeight;
    const percentageY = Math.round((y / imageHeight) * 100);

    const last_question = currentQuestion.last_question;
    const next_question_id = currentQuestion.next_question_id;
    const newTag = {
      ...currentTag,
      net: { x: percentageX, y: percentageY },
      netZone: zoneHovering,
    };

    advanceQuestion(last_question, next_question_id, newTag);
  };

  return (
    <div className="kaukalo-image-container">
      <img ref={imgRef} src={maali} alt="maali" className="kaukalo-image" />
      <canvas
        ref={canvasRef}
        onClick={handleCanvasClick}
        className="kaukalo-canvas"
      />
    </div>
  );
}
