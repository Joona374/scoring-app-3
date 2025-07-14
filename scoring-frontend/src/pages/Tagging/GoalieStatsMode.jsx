export default function GoalieStatsMode({ returnMethod }) {
  return (
    <div className="coming-soon-wrapper">
      <h1 className="coming-soon-h1">Tulossa pian!</h1>
      <button onClick={() => returnMethod()}>Takaisin</button>
    </div>
  );
}
