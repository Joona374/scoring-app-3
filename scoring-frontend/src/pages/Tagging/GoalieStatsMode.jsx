import MutedButton from "../../components/MutedButton/MutedButton";

export default function GoalieStatsMode({ returnMethod }) {
  return (
    <div className="coming-soon-wrapper">
      <h1 className="coming-soon-h1">Tulossa pian!</h1>
      <MutedButton text="Takaisin" onClickMethod={() => returnMethod()} />
    </div>
  );
}
