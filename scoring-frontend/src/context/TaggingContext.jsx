import { Question } from "../pages/Tagging/question";
import { createContext, useEffect, useState } from "react";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export const TaggingContext = createContext();

export const TaggingProvider = ({ children }) => {
  const [currentTag, setCurrentTag] = useState({});
  const [taggedEvents, setTaggedEvents] = useState([]);
  const [questionObjects, setQuestionObjects] = useState([]);
  const [currentQuestionId, setCurrentQuestionId] = useState(null);

  useEffect(() => {
    async function fetchQuestions() {
      const token = localStorage.getItem("jwt_token");

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
        if (questionObjs.length > 0) {
          setCurrentQuestionId(questionObjs[0].id);
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
      }}
    >
      {children}
    </TaggingContext.Provider>
  );
};
