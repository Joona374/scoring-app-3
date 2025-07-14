import "./ExcelExportSelector.css";

const mockExportOptions = [
  {
    id: "plusminus",
    title: "Pelaajakohtainen +/- raportti",
    description:
      "Raportti yksittäisen pelaajan +/- maalipaikka tilastoista. Raportti erittelee: 1. omat ja vastustajan maalit ja maalipaikat. 2. Kentällä ja osallisena olemisen. 3. 5vs5, ylivoima ja alivoima tilastot.",
  },
  {
    id: "team",
    title: "Joukkueraportti",
    description:
      "Yhdistetyt joukkueen tilastot pelien ajalta. Hyvä valmentajille kokonaiskuvan hahmottamiseen.",
  },
  {
    id: "goalies",
    title: "Maalivahtiraportti",
    description:
      "Kaikki torjunnat, päästetyt maalit ja laukaukset maalia kohti.",
  },
  {
    id: "custom",
    title: "Mukautettu raportti",
    description:
      "Valitse haluamasi tilastot ja muodosta räätälöity Excel-analyysi.",
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
