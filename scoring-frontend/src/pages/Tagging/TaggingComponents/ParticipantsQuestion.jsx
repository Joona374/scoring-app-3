import { useContext, useState, useEffect } from "react";
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

  // Add this useEffect:
  useEffect(() => {
    if (currentTag?.shooter) {
      const shooterId = currentTag.shooter.id;

      // Only add if not already set
      setOnIces((prev) =>
        prev.includes(shooterId) ? prev : [...prev, shooterId]
      );
      setParticipations((prev) =>
        prev.includes(shooterId) ? prev : [...prev, shooterId]
      );
    }
  }, [currentTag?.shooter]);

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
      <div className="participant-wrapper">
        <h2 className="participant-question-text">
          Osallistujat ja jäällä olleet
        </h2>
        <div className="participant-question-container">
          <div className="participant-left-column">
            {[1, 2, 3, 4].map((line) => {
              return (
                <div key={`d-row-${line}`} className="participant-d-row">
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
                          currentTag={currentTag}
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
                          currentTag={currentTag}
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
        <div className="participant-summary">
          <h3>Jäällä</h3>
          <ul>
            {onIces.map((id) => {
              const player = playersInRoster.find(
                (p) => p.player.id === id
              )?.player;
              return player ? (
                <li key={`on-ice-${id}`}>
                  {player.first_name} {player.last_name}
                </li>
              ) : null;
            })}
          </ul>

          <h3>Osallisena</h3>
          <ul>
            {participations.map((id) => {
              const player = playersInRoster.find(
                (p) => p.player.id === id
              )?.player;
              return player ? (
                <li key={`participated-${id}`}>
                  {player.first_name} {player.last_name}
                </li>
              ) : null;
            })}
          </ul>
        </div>

        <button className="confirm-button" onClick={handleSubmit}>
          Vahvista
        </button>
      </div>
    </>
  );
}
