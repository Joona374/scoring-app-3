import { useState, useRef, useEffect } from "react";
import { createPortal } from "react-dom";
import "./InfoTooltip.css";

export default function InfoTooltip({ text }) {
  const [visible, setVisible] = useState(false);
  const [coords, setCoords] = useState({ top: 0, left: 0 });
  const iconRef = useRef(null);

  const updateCoords = () => {
    if (iconRef.current) {
      const rect = iconRef.current.getBoundingClientRect();
      setCoords({
        top: rect.top + window.scrollY,
        left: rect.left + window.scrollX,
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
      {visible && createPortal(
        <div 
          className="info-balloon portal-balloon"
          style={{ 
            position: 'absolute',
            top: `${coords.top - 10}px`, // Slight offset above the icon
            left: `${coords.left + 20}px`, // Offset to the right
            transform: 'translateY(-100%)' // Move it above the point
          }}
        >
          {text}
        </div>,
        document.body
      )}
    </div>
  );
}
