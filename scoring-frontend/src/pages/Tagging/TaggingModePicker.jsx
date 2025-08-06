import MutedButton from "../../components/MutedButton/MutedButton";
import CreateGame from "../CreateGame/CreateGame";
import "./Styles/GamePicker.css";
MutedButton;

export default function TaggingModePicker({ setCurrentTaggingMode, onReturn }) {
  return (
    <div className="tagging-mode-picker-wrapper">
      <div className="game-picker-card">
        <h1>Valitse tilastointi pohja</h1>
        <p>Luo uusi peli tai jatka olemassa olevaa.</p>
        <div className="button-group">
          <button onClick={() => setCurrentTaggingMode("team")}>
            Joukkuetilastot
          </button>
          <button onClick={() => setCurrentTaggingMode("player")}>
            Pelaajatilastot
          </button>
          <button onClick={() => setCurrentTaggingMode("goalie")}>
            Maalivahtitilastot
          </button>
        </div>
      </div>
      <MutedButton
        text="Takaisin"
        onClickMethod={() => onReturn()}
      ></MutedButton>
    </div>
  );
}
