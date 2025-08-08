import { useContext, useEffect, useRef, useState } from "react";
import { TaggingContext } from "../../../context/TaggingContext";
import kaukalo from "../../../assets/kaukalo.png";
import "../Styles/ShotLocationQuestion.css";

export default function ShotLocationQuestion() {
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
      name: "BLUELINE",
      points: [
        // Blueline
        [0, 0],
        [100, 0],
        [100, 12],
        [0, 12],
      ],
    },
    {
      name: "HIGH_SLOT",
      points: [
        // Highslot
        [0, 11],
        [100, 11],
        [100, 23],
        [0, 23],
      ],
    },
    {
      name: "MISC",
      points: [
        // Pääty
        [0, 79],
        [100, 79],
        [100, 100],
        [0, 100],
      ],
    },
    {
      name: "OUTSIDE_CLOSE",
      points: [
        // Outside close left
        [50, 79],
        [25, 79],
        [25, 60],
      ],
    },
    {
      name: "OUTSIDE_FAR",
      points: [
        // Outside far left
        [0, 40],
        [25, 60],
        [25, 79],
        [0, 79],
      ],
    },
    {
      name: "ZONE_4",
      points: [
        // 4th Zone left
        [0, 23],
        [25, 23],
        [25, 60],
        [0, 40],
      ],
    },
    {
      name: "OUTSIDE_CLOSE",
      points: [
        // Outside close right
        [50, 79],
        [75, 79],
        [75, 60],
      ],
    },
    {
      name: "OUTSIDE_FAR",
      points: [
        // Outside far right
        [100, 40],
        [75, 60],
        [75, 79],
        [100, 79],
      ],
    },
    {
      name: "ZONE_4",
      points: [
        // 4th Zone right
        [100, 23],
        [75, 23],
        [75, 60],
        [100, 40],
      ],
    },
    {
      name: "ZONE_2_SIDE",
      points: [
        // 2nd Zone left
        [25, 23],
        [40, 23],
        [40, 50],
        [25, 60],
      ],
    },
    {
      name: "ZONE_2_MIDDLE",
      points: [
        // 2nd Zone middle
        [40, 23],
        [60, 23],
        [60, 50],
        [40, 50],
      ],
    },
    {
      name: "ZONE_2_SIDE",
      points: [
        // 2nd Zone left
        [75, 23],
        [60, 23],
        [60, 50],
        [75, 60],
      ],
    },
    {
      name: "ZONE_1",
      points: [
        // 1st Zone
        [50, 79],
        [25, 60],
        [40, 50],
        [60, 50],
        [75, 60],
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
          if (hoveredIndex !== null)
            setZoneHovering(shotZones[hoveredIndex].name);
          else setZoneHovering(null);
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

    // Derive the zone from the click position (don’t rely on hover state)
    const clickedZone = shotZones.find((z) =>
      pointInZone([percentageX, percentageY], z.points)
    );
    const zoneName = clickedZone ? clickedZone.name : null;

    const last_question = currentQuestion.last_question;
    const next_question_id = currentQuestion.next_question_id;
    const newTag = {
      ...currentTag,
      location: { x: percentageX, y: percentageY },
      shotZone: zoneName,
    };

    advanceQuestion(last_question, next_question_id, newTag);
  };

  return (
    <div className="kaukalo-image-container">
      <img ref={imgRef} src={kaukalo} alt="Kaukalo" className="kaukalo-image" />
      <canvas
        ref={canvasRef}
        onClick={handleCanvasClick}
        className="kaukalo-canvas"
      />
    </div>
  );
}
