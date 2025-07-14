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
  const [gamesForTeam, setGamesForTEam] = useState([]);

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
      setTaggedEvents((prev) => [...prev, fullTag]); // Safely append
      console.log("Latest tag: ", fullTag);
    } catch (error) {
      setTaggedEvents(rollbackTags);
      console.warn("Rolled tagged event back to:", rollbackTags);
      alert("Attention! Error posting tag. Changes have been reverted.");
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
        setGamesForTEam,
        currentTaggingMode,
        setCurrentTaggingMode,
        stepBackInTag,
      }}
    >
      {children}
    </TaggingContext.Provider>
  );
};
