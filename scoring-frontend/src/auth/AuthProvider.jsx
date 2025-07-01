import React, { useState, useEffect } from "react";
import AuthContext from "./AuthContext";

export function AuthProvider({ children }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = sessionStorage.getItem("jwt_token");
    if (token) {
      setIsLoggedIn(true);
    }
  }, []);

  const login = (token) => {
    setIsLoggedIn(true);
    sessionStorage.setItem("jwt_token", token);
  };

  const logout = () => {
    setIsLoggedIn(false);
    sessionStorage.clear();
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
