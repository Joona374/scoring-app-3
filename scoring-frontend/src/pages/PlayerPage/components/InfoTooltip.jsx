import { useState, useRef, useEffect } from "react";
import { createPortal } from "react-dom";
import "./InfoTooltip.css";

const TOOLTIP_WIDTH = 220;
const VIEWPORT_PADDING = 8;
const VERTICAL_OFFSET = 10;

export default function InfoTooltip({ text }) {
  const [visible, setVisible] = useState(false);
  const [coords, setCoords] = useState({ top: 0, left: 0, arrowLeft: 16 });
  const iconRef = useRef(null);

  const updateCoords = () => {
    if (iconRef.current) {
      const rect = iconRef.current.getBoundingClientRect();
      const scrollX = window.scrollX;
      const scrollY = window.scrollY;
      const preferredLeft =
        rect.left + scrollX + rect.width / 2 - TOOLTIP_WIDTH / 2;
      const minLeft = scrollX + VIEWPORT_PADDING;
      const maxLeft =
        scrollX + window.innerWidth - TOOLTIP_WIDTH - VIEWPORT_PADDING;
      const left = Math.min(
        Math.max(preferredLeft, minLeft),
        Math.max(minLeft, maxLeft),
      );
      const iconCenter = rect.left + scrollX + rect.width / 2;
      const arrowLeft = Math.min(
        Math.max(iconCenter - left, 12),
        TOOLTIP_WIDTH - 12,
      );

      setCoords({
        top: rect.top + scrollY,
        left,
        arrowLeft,
      });
    }
  };

  useEffect(() => {
    if (visible) {
      updateCoords();
      window.addEventListener('scroll', updateCoords);
      window.addEventListener('resize', updateCoords);
    }
    return () => {
      window.removeEventListener('scroll', updateCoords);
      window.removeEventListener('resize', updateCoords);
    };
  }, [visible]);

  return (
    <div
      className="info-tooltip-container"
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      onClick={() => setVisible(!visible)}
      ref={iconRef}
    >
      <span className="info-icon">?</span>
      {visible &&
        createPortal(
          <div
            className="info-balloon portal-balloon"
            style={{
              position: "absolute",
              top: `${coords.top - VERTICAL_OFFSET}px`,
              left: `${coords.left}px`,
              transform: "translateY(-100%)",
              "--arrow-left": `${coords.arrowLeft}px`,
            }}
          >
            {text}
          </div>,
          document.body,
        )}
    </div>
  );
}
