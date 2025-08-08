// src/pages/Analysis/Components/ResultBar.jsx
export default function ResultBar({ state, setState }) {
  const {
    show_cf,
    show_ca,
    show_gf,
    show_ga,
    show_sf,
    show_sa,
    strengths,
    mode,
  } = state;

  const toggle = (key) => setState((s) => ({ ...s, [key]: !s[key] }));
  const setMode = (m) => setState((s) => ({ ...s, mode: m }));

  const toggleStrength = (code) =>
    setState((s) => ({
      ...s,
      strengths: s.strengths.includes(code)
        ? s.strengths.filter((x) => x !== code)
        : [...s.strengths, code],
    }));

  const allPlus = () =>
    setState((s) => ({
      ...s,
      show_cf: true,
      show_gf: true,
      show_sf: true,
      show_ca: false,
      show_ga: false,
      show_sa: false,
    }));

  const allMinus = () =>
    setState((s) => ({
      ...s,
      show_cf: false,
      show_gf: false,
      show_sf: false,
      show_ca: true,
      show_ga: true,
      show_sa: true,
    }));

  // Map internal codes -> Finnish labels
  const strengthOptions = [
    { code: "ES", label: "TV" }, // tasaviisikoin
    { code: "PP", label: "YV" }, // ylivoima
    { code: "PK", label: "AV" }, // alivoima
    { code: "EN+", label: "TM+" }, // tyhjä maali meille
    { code: "EN-", label: "TM-" }, // tyhjä maali vastus
  ];

  return (
    <div className="card resultbar">
      {/* Results */}
      <div className="rb-group rb-results">
        <span className="rb-label">Tulokset</span>

        {/* + side */}
        <div className="rb-side">
          <button className="pill xs pill-ghost" onClick={allPlus}>
            +
          </button>
          <button
            className={`pill xs ${show_cf ? "pill-active" : ""}`}
            onClick={() => toggle("show_cf")}
          >
            MP +
          </button>
          <button
            className={`pill xs ${show_gf ? "pill-active" : ""}`}
            onClick={() => toggle("show_gf")}
          >
            Maali +
          </button>
          <button
            className={`pill xs ${show_sf ? "pill-active" : ""}`}
            onClick={() => toggle("show_sf")}
          >
            Laukaus +
          </button>
        </div>

        <div className="rb-divider" />

        {/* - side */}
        <div className="rb-side">
          <button className="pill xs pill-ghost" onClick={allMinus}>
            −
          </button>
          <button
            className={`pill xs ${show_ca ? "pill-active" : ""}`}
            onClick={() => toggle("show_ca")}
          >
            MP −
          </button>
          <button
            className={`pill xs ${show_ga ? "pill-active" : ""}`}
            onClick={() => toggle("show_ga")}
          >
            Maali −
          </button>
          <button
            className={`pill xs ${show_sa ? "pill-active" : ""}`}
            onClick={() => toggle("show_sa")}
          >
            Laukaus −
          </button>
        </div>
      </div>

      {/* Strengths (Finnish labels, same codes) */}
      <div className="rb-group">
        <span className="rb-label">Pelitilanne</span>
        {strengthOptions.map(({ code, label }) => (
          <button
            key={code}
            className={`pill xs ${
              strengths.includes(code) ? "pill-active" : ""
            }`}
            onClick={() => toggleStrength(code)}
            title={code} // hover shows underlying code if you want
          >
            {label}
          </button>
        ))}
      </div>

      {/* View */}
      <div className="rb-group">
        <span className="rb-label">Näkymä</span>
        <button
          className={`pill xs ${mode === "heatmap" ? "pill-active" : ""}`}
          onClick={() => setMode("heatmap")}
        >
          Heatmap
        </button>
        <button
          className={`pill xs ${mode === "scatter" ? "pill-active" : ""}`}
          onClick={() => setMode("scatter")}
        >
          Pisteinä
        </button>
      </div>
    </div>
  );
}
