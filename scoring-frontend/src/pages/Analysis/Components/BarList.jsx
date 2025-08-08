// src/components/analysis/BarList.jsx
export default function BarList({
  title,
  dataObj,
  dataArr,
  keyField,
  valField,
}) {
  const items = dataObj
    ? Object.entries(dataObj).map(([k, v]) => ({ key: k, val: v }))
    : (dataArr || []).map((row) => ({
        key: row[keyField],
        val: row[valField],
      }));
  const max = Math.max(1, ...items.map((i) => i.val));

  return (
    <div className="card">
      <h3>{title}</h3>
      <div className="bars">
        {items.length === 0 && <div className="muted">No data</div>}
        {items.map(({ key, val }) => (
          <div className="bar-row" key={key}>
            <span className="bar-label">{key}</span>
            <div className="bar-track">
              <div
                className="bar-fill"
                style={{ width: `${(val / max) * 100}%` }}
              />
            </div>
            <span className="bar-val">{val}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
