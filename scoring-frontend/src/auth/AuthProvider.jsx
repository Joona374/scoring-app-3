import React, { useState, useEffect } from "react";
import AuthContext from "./AuthContext";

export function AuthProvider({ children }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("jwt_token");
    if (token) {
      setIsLoggedIn(true);
    }
  }, []);

  const login = (token) => {
    setIsLoggedIn(true);
    localStorage.setItem("jwt_token", token);
  };

  const logout = () => {
    setIsLoggedIn(false);
    localStorage.removeItem("jwt_token");
  };

  const authData = {
    isLoggedIn,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={authData}>{children}</AuthContext.Provider>
  );
}
