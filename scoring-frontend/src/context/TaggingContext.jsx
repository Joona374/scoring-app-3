import { Question } from "../pages/Tagging/question";
import { createContext, use, useEffect, useState } from "react";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export const TaggingContext = createContext();

export const TaggingProvider = ({ children }) => {
  const [currentTag, setCurrentTag] = useState({});
  const [taggedEvents, setTaggedEvents] = useState([]);
  const [questionObjects, setQuestionObjects] = useState([]);
  const [currentQuestionId, setCurrentQuestionId] = useState(null);
  const [firstQuestionId, setFirstQuestionId] = useState(null);
  const [playersInRoster, setPlayersInRoster] = useState([]);
  const [currentGameId, setCurrentGameId] = useState();
  const [gamesForTeam, setGamesForTEam] = useState([]);

  console.log("In provider - setCurrentGameId type:", typeof setCurrentGameId);

  const advanceQuestion = (last_question, next_question_id, newTag) => {
    try {
      if (last_question === true) {
        const rollbackTags = [...taggedEvents];
        const new_tagged_events = [...taggedEvents, newTag];
        setTaggedEvents(new_tagged_events);
        console.log("This is the latest tagged events: ", new_tagged_events);
        postTag(newTag, rollbackTags);
        setCurrentTag({});
        setCurrentQuestionId(firstQuestionId);
      } else {
        setCurrentTag(newTag);
        setCurrentQuestionId(next_question_id);
      }
    } catch (error) {
      console.log("error");
    }
  };

  const postTag = async (newTag, rollbackTags) => {
    const token = sessionStorage.getItem("jwt_token");
    newTag.game_id = currentGameId;

    try {
      const res = await fetch(`${BACKEND_URL}/tagging/add-team-tag`, {
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
      console.log("data for tag: ", data);
    } catch (error) {
      setTaggedEvents(rollbackTags);
      console.warn("Rolled tagged event back to:", rollbackTags);
      alert("Attention! Error posting tag. Changes have been reverted.");
    }
  };

  useEffect(() => {
    async function fetchQuestions() {
      const token = sessionStorage.getItem("jwt_token");

      try {
        const res = await fetch(`${BACKEND_URL}/tagging/questions`, {
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
        console.log(questionObjs);
        if (questionObjs.length > 0) {
          // TODO: CHANGING THIS BACK TO questionObjs[0]. This is just for dev
          setCurrentQuestionId(questionObjs[0].id);
          setFirstQuestionId(questionObjs[0].id);
        }
      } catch (err) {
        console.error("Error fetching questions from backend:", err);
      }
    }
    fetchQuestions();
  }, []);

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
      }}
    >
      {children}
    </TaggingContext.Provider>
  );
};
