import { Question } from "../pages/Tagging/question";
import { createContext, use, useEffect, useState } from "react";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export const TaggingContext = createContext();

export const TaggingProvider = ({ children }) => {
  const [currentTag, setCurrentTag] = useState({});
  const [taggedEvents, setTaggedEvents] = useState([]);
  const [questionObjects, setQuestionObjects] = useState([]);
  const [currentQuestionId, setCurrentQuestionId] = useState(null);
  const [previousQuestionsQueue, setPreviousQuestionsQueue] = useState([]);
  const [currentTaggingMode, setCurrentTaggingMode] = useState("");
  const [firstQuestionId, setFirstQuestionId] = useState(null);
  const [playersInRoster, setPlayersInRoster] = useState([]);
  const [currentGameId, setCurrentGameId] = useState();
  const [gamesForTeam, setGamesForTeam] = useState([]);
  const [playersInTeam, setPlayersInTeam] = useState([]);

  const advanceQuestion = (last_question, next_question_id, newTag) => {
    try {
      if (last_question === true) {
        const rollbackTags = [...taggedEvents];
        postTag(newTag, rollbackTags);
        setCurrentTag({});
        setCurrentQuestionId(firstQuestionId);
        setPreviousQuestionsQueue([]);
      } else {
        setCurrentTag(newTag);
        const newPreviousQuestionsQueue = [
          ...previousQuestionsQueue,
          currentQuestionId,
        ];
        setPreviousQuestionsQueue(newPreviousQuestionsQueue);
        setCurrentQuestionId(next_question_id);
      }
    } catch (error) {
      console.log("error", error);
    }
  };

  const postTag = async (newTag, rollbackTags) => {
    const token = sessionStorage.getItem("jwt_token");
    newTag.game_id = currentGameId;

    let postingEndpoint;
    if (currentTaggingMode === "team")
      postingEndpoint = `${BACKEND_URL}/tagging/add-team-tag`;
    else if (currentTaggingMode === "player")
      postingEndpoint = `${BACKEND_URL}/tagging/add-players-tag`;
    // TODO: IMPLEMENT THIS ENDPOINT TO BACKEND
    else if (currentTaggingMode === "goaie")
      postingEndpoint = `${BACKEND_URL}/tagging/add-goalies-tag`;

    console.log("NEW TAG BEFORE POSTNG:", newTag);

    try {
      const res = await fetch(postingEndpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ tag: newTag }),
      });

      if (!res.ok) {
        console.error(res);
        setTaggedEvents(rollbackTags);
        console.warn("Rolled tagged event back to:", rollbackTags);
        return;
      }
      const data = await res.json();
      const fullTag = { ...newTag, id: data.id }; // Merge ID into tag
      console.log("Tag posted successfully:", fullTag);
      setTaggedEvents((prev) => [...prev, fullTag]); // Safely append
    } catch (error) {
      setTaggedEvents(rollbackTags);
      console.warn("Rolled tagged event back to:", rollbackTags);
      alert("Huomio! Virhe tägin lähetyksessä. Muutokset on peruttu.");
    }
  };

  const stepBackInTag = () => {
    const previousQuestionId =
      previousQuestionsQueue[previousQuestionsQueue.length - 1];
    const previousQuestion = questionObjects.find(
      (questionObject) => questionObject.id === previousQuestionId
    );
    const newTag = { ...currentTag };
    delete newTag[previousQuestion.key];

    setCurrentTag(newTag);
    setCurrentQuestionId(previousQuestionId);
    setPreviousQuestionsQueue(previousQuestionsQueue.slice(0, -1));
  };

  const getGamesFromBackend = async () => {
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
    const token = sessionStorage.getItem("jwt_token");

    try {
      const res = await fetch(`${BACKEND_URL}/games/get-for-user`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) {
        console.log(
          "Getting a list of games to continue from the server failed."
        );
      }

      const data = await res.json();
      setGamesForTeam(data);
    } catch (err) {
      console.log(err);
    }
  };

  const fetchPlayersInTeam = async () => {
    try {
      const token = sessionStorage.getItem("jwt_token");
      const res = await fetch(`${BACKEND_URL}/players/for-team`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) {
        throw new Error("Failed to fetch players for users teams");
      }

      const players = await res.json();
      setPlayersInTeam(players);
    } catch (error) {
      console.log("Error?: ", error);
      throw new Error("Failed to fetch players for users teams");
    }
  };

  return (
    <TaggingContext.Provider
      value={{
        currentTag,
        setCurrentTag,
        taggedEvents,
        setTaggedEvents,
        questionObjects,
        setQuestionObjects,
        currentQuestionId,
        setCurrentQuestionId,
        firstQuestionId,
        setFirstQuestionId,
        advanceQuestion,
        playersInRoster,
        setPlayersInRoster,
        currentGameId,
        setCurrentGameId,
        gamesForTeam,
        setGamesForTeam,
        currentTaggingMode,
        setCurrentTaggingMode,
        stepBackInTag,
        getGamesFromBackend,
        fetchPlayersInTeam,
        playersInTeam,
      }}
    >
      {children}
    </TaggingContext.Provider>
  );
};
