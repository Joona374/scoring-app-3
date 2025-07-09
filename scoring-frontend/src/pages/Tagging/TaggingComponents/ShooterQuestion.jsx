import { useContext } from "react";
import { TaggingContext } from "../../../context/TaggingContext";
import PlayerBox from "./PlayerBox";
import "../Styles/ShooterQuestion.css";

export default function ShooterQuestion() {
  const {
    currentTag,
    setCurrentTag,
    setQuestionId,
    playersInRoster,
    advanceQuestion,
    currentQuestionId,
    questionObjects,
  } = useContext(TaggingContext);

  const currentQuestion = questionObjects.find(
    (q) => q.id === currentQuestionId
  );

  return (
    <>
      <p>Shooter question</p>
      <div className="shooter-question-container">
        <div className="shooter-left-column">
          {[1, 2, 3, 4].map((line) => {
            return (
              <div key={`d-row-${line}`} className="shooter-f-row">
                {["LD", "RD"].map((position) => {
                  const playerForPosition = playersInRoster.find(
                    (posInRoster) =>
                      posInRoster.line === line &&
                      posInRoster.position === position
                  );

                  if (playerForPosition) {
                    const player = playerForPosition.player;
                    return (
                      <PlayerBox
                        key={`${line}-${position}`}
                        name={`${player.first_name} ${player.last_name}`}
                        pos="DEFENDER"
                        player={player}
                        setCurrentTag={setCurrentTag}
                        prevTag={currentTag}
                        advanceQuestion={advanceQuestion}
                        question={currentQuestion}
                      ></PlayerBox>
                    );
                  } else {
                    return (
                      <PlayerBox
                        key={`${line}-${position}`}
                        name={"--"}
                        pos="DEFENDER"
                        player={null}
                        setCurrentTag={setCurrentTag}
                        prevTag={currentTag}
                        advanceQuestion={advanceQuestion}
                        question={currentQuestion}
                      ></PlayerBox>
                    );
                  }
                })}
              </div>
            );
          })}
        </div>
        <div className="shooter-right-column">
          {[1, 2, 3, 4, 5].map((line) => {
            return (
              <div className="shooter-f-row" key={`f-row-${line}`}>
                {["LW", "C", "RW"].map((position) => {
                  const playerForPosition = playersInRoster.find(
                    (posInRoster) =>
                      posInRoster.line === line &&
                      posInRoster.position === position
                  );

                  if (playerForPosition) {
                    const player = playerForPosition.player;
                    return (
                      <PlayerBox
                        key={`${line}-${position}`}
                        name={`${player.first_name} ${player.last_name}`}
                        pos={"FORWARD"}
                        player={player}
                        setCurrentTag={setCurrentTag}
                        prevTag={currentTag}
                        advanceQuestion={advanceQuestion}
                        question={currentQuestion}
                      ></PlayerBox>
                    );
                  } else {
                    return (
                      <PlayerBox
                        key={`${line}-${position}`}
                        name={"--"}
                        pos={"FORWARD"}
                        player={null}
                        setCurrentTag={setCurrentTag}
                        prevTag={currentTag}
                        advanceQuestion={advanceQuestion}
                        question={currentQuestion}
                      ></PlayerBox>
                    );
                  }
                })}
              </div>
            );
          })}
        </div>
      </div>
    </>
  );
}
