import React, { useState } from "react";
import AuthContext from "./AuthContext";

export function AuthProvider({ children }) {

    const [isLoggedIn, setIsLoggedIn] = useState(false);

    const authData = {
        isLoggedIn,
        login: () => setIsLoggedIn(true),
        logout: () => setIsLoggedIn(false)
    };

    return (
    <AuthContext.Provider value={authData}>
      {children}
    </AuthContext.Provider>
  );
}