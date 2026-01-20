// src/pages/Analysis/Components/Analysis.jsx
import { useEffect, useMemo, useState } from "react";
import KPIs from "./KPIs";
import BarList from "./BarList";
import IceMap from "./IceMap";
import NetMap from "./NetMap";
import "../Analysis.css";

export default function Analysis({ params }) {
  const [data, setData] = useState(null);
  const [mode, setMode] = useState("scatter"); // "heatmap" | "scatter" - default to scatter

  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
  const token = sessionStorage.getItem("jwt_token");

  useEffect(() => {
    const load = async () => {
      const qs = new URLSearchParams();
      qs.set("game_ids", params.game_ids.join(","));
      if (params.shooter_ids?.length)
        qs.set("shooter_ids", params.shooter_ids.join(","));
      if (params.strengths?.length)
        qs.set("strengths", params.strengths.join(","));
      if (params.shot_types?.length)
        qs.set("shot_types", params.shot_types.join(","));
      qs.set("show_cf", params.show_cf);
      qs.set("show_ca", params.show_ca);
      qs.set("show_gf", params.show_gf);
      qs.set("show_ga", params.show_ga);

      const res = await fetch(`${BACKEND_URL}/analysis?${qs.toString()}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const json = await res.json();
      setData(json);
    };
    load();
  }, [JSON.stringify(params)]);

  const [showFor, setShowFor] = useState(true);
  const [showAgainst, setShowAgainst] = useState(true);
  const [onlyGoals, setOnlyGoals] = useState(false);

  const filteredIce = useMemo(() => {
    if (!data) return [];
    return data.ice_points.filter((p) => {
      if (!showFor && p.side === "FOR") return false;
      if (!showAgainst && p.side === "AGAINST") return false;
      if (onlyGoals && !p.is_goal) return false;
      return true;
    });
  }, [data, showFor, showAgainst, onlyGoals]);

  const filteredNet = useMemo(() => {
    if (!data) return [];
    return data.net_points.filter((p) => {
      if (!showFor && p.side === "FOR") return false;
      if (!showAgainst && p.side === "AGAINST") return false;
      if (onlyGoals && !p.is_goal) return false;
      return true;
    });
  }, [data, showFor, showAgainst, onlyGoals]);

  if (!data)
    return (
      <div className="card" style={{ marginTop: 12 }}>
        Loading…
      </div>
    );

  return (
    <div className="ana-grid">
      <div className="card controls">
        {/* Heatmap/Scatter toggle removed - always use scatter mode */}
        <div className="toggle-group">
          <label className="chk">
            <input
              type="checkbox"
              checked={showFor}
              onChange={(e) => setShowFor(e.target.checked)}
            />{" "}
            <span>Show For</span>
          </label>
          <label className="chk">
            <input
              type="checkbox"
              checked={showAgainst}
              onChange={(e) => setShowAgainst(e.target.checked)}
            />{" "}
            <span>Show Against</span>
          </label>
          <label className="chk">
            <input
              type="checkbox"
              checked={onlyGoals}
              onChange={(e) => setOnlyGoals(e.target.checked)}
            />{" "}
            <span>Only goals</span>
          </label>
        </div>
      </div>

      <KPIs totals={data.totals} />

      <div className="ana-row">
        <IceMap title="Ice Map" mode={mode} points={filteredIce} />
        <NetMap title="Net Map" mode={mode} points={filteredNet} />
      </div>

      <div className="ana-row">
        <BarList title="Shot Result" dataObj={data.by_result} />
        <BarList title="Shot Type" dataObj={data.by_type} />
        <BarList title="Strengths" dataObj={data.by_strengths} />
      </div>

      <div className="ana-row">
        <BarList title="Cross-ice" dataObj={data.crossice} />
        <BarList
          title="Net Zones"
          dataArr={data.net_bins}
          keyField="zone"
          valField="count"
        />
      </div>
    </div>
  );
}
