import { useEffect, useMemo, useState } from "react";
import KPIs from "./KPIs";
import BarList from "./BarList";
import IceMap from "./IceMap";
import NetMap from "./NetMap";
import LoadingSpinner from "../../../components/LoadingSpinner/LoadingSpinner";

export default function AnalysisBody({ params }) {
  const [data, setData] = useState(null);
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
      qs.set("show_cf", params.show_cf);
      qs.set("show_ca", params.show_ca);
      qs.set("show_gf", params.show_gf);
      qs.set("show_ga", params.show_ga);
      qs.set("show_sf", params.show_sf);
      qs.set("show_sa", params.show_sa);

      const res = await fetch(`${BACKEND_URL}/analysis?${qs.toString()}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const json = await res.json();
      setData(json);
    };
    load();
  }, [JSON.stringify(params)]);

  const filteredIce = data ? data.ice_points : [];
  const filteredNet = data ? data.net_points : [];

  if (!data) return LoadingSpinner(25);

  return (
    <div className="ana-grid">
      <KPIs totals={data.totals} />

      <div className="ana-row">
        <IceMap title="Ice Map" mode={params.mode} points={filteredIce} />
        <NetMap title="Net Map" mode={params.mode} points={filteredNet} />
      </div>

      {/* <div className="ana-row">
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
      </div> */}
    </div>
  );
}
