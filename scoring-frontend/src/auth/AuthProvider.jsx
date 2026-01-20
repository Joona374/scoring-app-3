import React, { useState, useEffect } from "react";
import AuthContext from "./AuthContext";
import { clearDashboardCache } from "../utils/dashboardCache";

export function AuthProvider({ children }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

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
    setIsAdmin(false);
    sessionStorage.clear();
    clearDashboardCache(); // Clear cached dashboard data on logout
  };

  const authData = {
    isLoggedIn,
    isAdmin,
    login,
    logout,
    setIsAdmin,
  };

  return (
    <AuthContext.Provider value={authData}>{children}</AuthContext.Provider>
  );
}
