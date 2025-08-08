// src/pages/Analysis/Components/NetMap.jsx
import netImg from "../../../assets/maali.jpg";
import MapCanvas from "./MapCanvas";

export default function NetMap({ title, mode, points }) {
  return (
    <div className="card">
      <MapCanvas img={netImg} points={points} mode={mode} heatRadius={16} />
    </div>
  );
}
