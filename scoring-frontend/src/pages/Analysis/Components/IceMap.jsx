// src/pages/Analysis/Components/IceMap.jsx
import rinkImg from "../../../assets/kaukalo.png";
import MapCanvas from "./MapCanvas";

export default function IceMap({ title, mode, points }) {
  return (
    <div className="card">
      <MapCanvas img={rinkImg} points={points} mode={mode} heatRadius={24} />
    </div>
  );
}
