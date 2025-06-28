import { createContext, useState } from "react";

export const TaggingContext = createContext();

export const TaggingProvider = ({ children }) => {
  const [currentTag, setCurrentTag] = useState({});
  const [taggedEvents, setTaggedEvents] = useState([]);

  return (
    <TaggingContext.Provider
      value={{ currentTag, setCurrentTag, taggedEvents, setTaggedEvents }}
    >
      {children}
    </TaggingContext.Provider>
  );
};
