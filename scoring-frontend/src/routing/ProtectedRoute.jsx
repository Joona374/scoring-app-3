import { useContext } from "react";
import { Navigate } from "react-router-dom";
import AuthContext from "../auth/AuthContext";

export default function ProtectRoute({ children }) {
  const { isLoggedIn } = useContext(AuthContext);

  if (!isLoggedIn) {
    return <Navigate to="/" replace />;
  }

  return children;
}
