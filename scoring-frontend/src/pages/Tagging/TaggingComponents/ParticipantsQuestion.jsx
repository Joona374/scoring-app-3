import { useContext, useState } from "react";
import { TaggingContext } from "../../../context/TaggingContext";
import ParticipantBox from "./ParticipantBox";
import "../Styles/ParticipantQuestion.css";

export default function ParticapntsQuestion() {
  const {
    currentTag,
    setCurrentTag,
    setQuestionId,
    playersInRoster,
    setPlayersInRoster,
    advanceQuestion,
    currentQuestionId,
    questionObjects,
  } = useContext(TaggingContext);

  // Get the current question using the currentQuestionId
  const currentQuestion = questionObjects.find(
    (q) => q.id === currentQuestionId
  );

  const [onIces, setOnIces] = useState([]);
  const [participations, setParticipations] = useState([]);

  const clickPlayer = (player) => {
    const playerId = player.id;
    const wasOnIce = onIces.includes(playerId);
    const participates = participations.includes(playerId);
    if (participates) {
      const filteredParticipations = participations.filter(
        (id) => id !== playerId
      );
      setParticipations(filteredParticipations);
      const filteredOnIces = onIces.filter((id) => id !== playerId);
      setOnIces(filteredOnIces);
    } else if (wasOnIce) {
      const newParticipations = [...participations, playerId];
      setParticipations(newParticipations);
    } else {
      const newOnIces = [...onIces, playerId];
      setOnIces(newOnIces);
    }
  };

  const handleSubmit = () => {
    const newCurrentTag = {
      ...currentTag,
      on_ices: onIces,
      participations: participations,
    };
    advanceQuestion(
      currentQuestion.last_question,
      currentQuestion.next_question_id,
      newCurrentTag
    );
  };

  return (
    <>
      <p>Shooter question</p>
      <div className="participant-question-container">
        <div className="participant-left-column">
          {[1, 2, 3, 4].map((line) => {
            return (
              <div key={`d-row-${line}`} className="participant-f-row">
                {["LD", "RD"].map((position) => {
                  const playerForPosition = playersInRoster.find(
                    (posInRoster) =>
                      posInRoster.line === line &&
                      posInRoster.position === position
                  );

                  if (playerForPosition) {
                    const thisPlayer = playerForPosition.player;
                    return (
                      <ParticipantBox
                        key={`${line}-${position}`}
                        player={thisPlayer}
                        clickHandler={(player) => {
                          clickPlayer(player);
                        }}
                        participants={participations}
                        onIces={onIces}
                      ></ParticipantBox>
                    );
                  } else {
                    return (
                      <ParticipantBox
                        key={`${line}-${position}`}
                        player={null}
                      ></ParticipantBox>
                    );
                  }
                })}
              </div>
            );
          })}
        </div>
        <div className="participant-right-column">
          {[1, 2, 3, 4, 5].map((line) => {
            return (
              <div className="participant-f-row" key={`f-row-${line}`}>
                {["LW", "C", "RW"].map((position) => {
                  const playerForPosition = playersInRoster.find(
                    (posInRoster) =>
                      posInRoster.line === line &&
                      posInRoster.position === position
                  );

                  if (playerForPosition) {
                    const thisPlayer = playerForPosition.player;
                    return (
                      <ParticipantBox
                        key={`${line}-${position}`}
                        player={thisPlayer}
                        clickHandler={(player) => {
                          clickPlayer(player);
                        }}
                        participants={participations}
                        onIces={onIces}
                      ></ParticipantBox>
                    );
                  } else {
                    return (
                      <ParticipantBox
                        key={`${line}-${position}`}
                        player={null}
                      ></ParticipantBox>
                    );
                  }
                })}
              </div>
            );
          })}
        </div>
      </div>
      <button onClick={() => handleSubmit()}>Confirm</button>
    </>
  );
}
