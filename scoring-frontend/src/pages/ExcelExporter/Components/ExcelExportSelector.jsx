import "./ExcelExportSelector.css";

const mockExportOptions = [
  {
    id: "team",
    title: "Joukkueen maalipaikkaraportti",
    description: "",
  },
  {
    id: "plusminus",
    title: "Pelaajien + / - raportti",
    description: "",
  },
  {
    id: "playersSummary",
    title: "Pelaajien maalipaikka yhteenveto",
    description: "",
  },

  {
    id: "games",
    title: "Peliraportit",
    description: "",
  },
];

export default function ExcelExportSelector({ selectedId, onSelect }) {
  return (
    <div className="export-selector">
      <h2 className="selector-title">Valitse raportti</h2>
      {mockExportOptions.map((option) => (
        <div
          key={option.id}
          className={`export-card ${
            selectedId === option.id ? "selected" : ""
          }`}
          onClick={() => onSelect(option.id)}
        >
          <h3>{option.title}</h3>
          <p>{option.description}</p>
        </div>
      ))}
    </div>
  );
}
