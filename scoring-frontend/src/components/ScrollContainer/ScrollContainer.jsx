import React from "react";
import "./ScrollContainer.css";

export default function ScrollContainer({ children, className = "", style = {}, maxHeight }) {
  const combinedStyle = { ...style };
  if (maxHeight) combinedStyle.maxHeight = maxHeight;

  const classes = ["scroll-container", className].filter(Boolean).join(" ");

  return (
    <div className={classes} style={combinedStyle}>
      {children}
    </div>
  );
}
