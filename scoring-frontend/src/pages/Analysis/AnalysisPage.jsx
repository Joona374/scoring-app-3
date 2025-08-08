// src/Pages/Analysis/AnalysisPage.jsx
import { useState } from "react";
import "./Analysis.css";
import FilterAccordion from "./Components/FilterAccordion";
import ResultBar from "./Components/ResultBar";
import AnalysisBody from "./Components/AnalysisBody";

export default function AnalysisPage() {
  const [filterParams, setFilterParams] = useState(null); // { game_ids:[], shooter_ids:[] }
  const [resultBar, setResultBar] = useState({
    show_cf: true,
    show_ca: true,
    show_gf: true,
    show_ga: true,
    show_sf: true,
    show_sa: true,
    strengths: ["ES", "PP", "PK", "EN+", "EN-"],
    mode: "heatmap", // "scatter"
  });

  return (
    <div className="analysis-page">
      <FilterAccordion onApply={setFilterParams} />
      <ResultBar state={resultBar} setState={setResultBar} />
      {filterParams ? (
        <AnalysisBody params={{ ...filterParams, ...resultBar }} />
      ) : (
        <div className="card hint">Select at least one game to begin.</div>
      )}
    </div>
  );
}
