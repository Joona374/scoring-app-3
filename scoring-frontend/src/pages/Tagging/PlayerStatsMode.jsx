import { useContext, useEffect, useState } from "react";
import { TaggingContext } from "../../context/TaggingContext";

import ShotLocationQuestion from "./TaggingComponents/ShotLocationQuestion";
import GridChoiceQuestion from "./TaggingComponents/GridChoiceQuestion";
import ShooterQuestion from "./TaggingComponents/ShooterQuestion";
import "./Styles/TaggingArea.css";
import NetQuestion from "./TaggingComponents/NetQuestion";
import ParticapntsQuestion from "./TaggingComponents/ParticipantsQuestion";
import PlayerTaggingSummary from "./PlayerTaggingSummary";
import BasicButton from "../../components/BasicButton/BasicButton";
import Modal from "../../components/Modal/Modal";
import RosterSelector from "../../components/RosterSelector/RosterSelector";

import { Question } from "./question";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function PlayerStatsMode({}) {
  const {
    setTaggedEvents,
    questionObjects,
    setQuestionObjects,
    currentQuestionId,
    setCurrentQuestionId,
    playersInTeam,
    fetchPlayersInTeam,
    playersInRoster,
    setPlayersInRoster,
    currentGameId,
    setFirstQuestionId,
    stepBackInTag,
  } = useContext(TaggingContext);

  const [showRosterEditor, setShowRosterEditor] = useState(false);
  const [game, setGame] = useState(null);

  useEffect(() => {
    fetchPlayersInTeam();
    fetchQuestions();
    fetchTags();
    async function asyncFetchGame() {
      const game = await fetchGame();
      console.log("Game:", game);
      setGame(game);
    }
    asyncFetchGame();
  }, []);

  async function fetchGame() {
    const token = sessionStorage.getItem("jwt_token");
    const gameId = currentGameId;
    try {
      const res = await fetch(`${BACKEND_URL}/games/get/${gameId}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      const gameJson = await res.json();
      return gameJson;
    } catch (err) {
      console.error("Error fetching game from backend:", err);
    }
  }

  async function fetchQuestions() {
    const token = sessionStorage.getItem("jwt_token");

    try {
      const res = await fetch(`${BACKEND_URL}/tagging/questions/player`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      const questionsJson = await res.json();
      const questionObjs = questionsJson.questions.map(
        (element) => new Question(element)
      );
      setQuestionObjects(questionObjs);
      if (questionObjs.length > 0) {
        setCurrentQuestionId(questionObjs[0].id);
        setFirstQuestionId(questionObjs[0].id);
      }
    } catch (err) {
      console.error("Error fetching questions from backend:", err);
    }
  }

  async function fetchTags() {
    const token = sessionStorage.getItem("jwt_token");
    const queryString = `${BACKEND_URL}/tagging/load/player-tags/${currentGameId}`;

    try {
      const res = await fetch(queryString, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) {
        console.log("Error downloading tags for game:", currentGameId);
      }

      const data = await res.json();
      setTaggedEvents(data);
    } catch (err) {
      console.log(err);
    }
  }

  // This function gets the roster for this game form db
  const getRosterFromDb = async (gameId) => {
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
    const token = sessionStorage.getItem("jwt_token");

    try {
      const res = await fetch(
        `${BACKEND_URL}/tagging/roster-for-game?game_id=${gameId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!res.ok) {
        console.log(
          "no work getting roster for game (IS IT 1? Forgot to change?):",
          gameId
        );
      }

      const data = await res.json();
      setPlayersInRoster(data);
    } catch (err) {
      console.log(err);
    }
  };

  useEffect(() => {
    if (currentGameId) getRosterFromDb(currentGameId);
  }, [currentGameId]);

  // Get the current question using the currentQuestionId
  const currentQuestion = questionObjects.find(
    (q) => q.id === currentQuestionId
  );

  // If no currentQuestion (still fecthing) display Loading...
  if (!currentQuestion) return <p>Loading...</p>;

  const renderQuestionComponent = () => {
    switch (currentQuestion.type) {
      case "SHOT LOCATION":
        return <ShotLocationQuestion />;
      case "NET LOCATION":
        return <NetQuestion />;
      case "TEXT":
        return <GridChoiceQuestion />;
      case "SHOOTER":
        console.log(playersInRoster);
        return <ShooterQuestion />;
      case "PARTICIPANTS":
        return <ParticapntsQuestion />;
      default:
        return <p>Unknow question type</p>;
    }
  };

  const updateRoster = async (newRoster) => {
    setPlayersInRoster(newRoster);

    // This could be a PUT or PATCH request to your backend API
    const response = await fetch(
      `${BACKEND_URL}/tagging/roster-for-game?game_id=${currentGameId}`,
      {
        method: "PUT", // or "PATCH" depending on your API design
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionStorage.getItem("jwt_token")}`,
        },
        body: JSON.stringify(newRoster),
      }
    );

    if (!response.ok) {
      console.error("Failed to update roster in the database");
      // Optionally, you could revert the local state change if the update fails
    } else {
      console.log("Roster updated successfully in the database");
    }
  };

  return (
    <div className="tagging-page">
      <div className="tagging-area-column">
        {renderQuestionComponent()}
        <button className={"tagging-back-button"} onClick={stepBackInTag}>
          {"<="}
        </button>{" "}
      </div>
      <div className="tagging-summary-column">
        <PlayerTaggingSummary></PlayerTaggingSummary>
        <BasicButton
          text="Muokkaa kokoonpanoa"
          onClickMethod={() => setShowRosterEditor(true)}
        />
      </div>

      {showRosterEditor && (
        <Modal
          children={
            <RosterSelector
              setShowRosterSelector={setShowRosterEditor}
              playersInTeam={playersInTeam}
              playersInRoster={playersInRoster}
              updateRoster={updateRoster}
              homeGame={game ? game.home_game : null}
            />
          }
        ></Modal>
      )}
    </div>
  );
}
