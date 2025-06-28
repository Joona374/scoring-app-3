import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home/Home";
import Login from "./pages/Login/Login";
import Register from "./pages/Register/Register";
import Dashboard from "./pages/Dashboard/Dashboard";
import ProtectRoute from "./routing/ProtectedRoute";
import Navbar from "./components/navbar/Navbar";
import CreateTeam from "./pages/CreateTeam/CreateTeam";
import CreatePlayer from "./pages/CreatePlayer/CreatePlayer";
import Tagging from "./pages/Tagging/Tagging";

function App() {
  return (
    <div>
      <Navbar></Navbar>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/dashboard"
          element={
            <ProtectRoute>
              <Dashboard />
            </ProtectRoute>
          }
        />
        {/* TODO: PROTECT THESE ROUTER */}
        <Route
          path="/create-team"
          element={
            <ProtectRoute>
              <CreateTeam />
            </ProtectRoute>
          }
        />
        <Route
          path="/create-player"
          element={
            <ProtectRoute>
              <CreatePlayer />
            </ProtectRoute>
          }
        />
        <Route
          path="/tagging"
          element={
            <ProtectRoute>
              <Tagging />
            </ProtectRoute>
          }
        />
      </Routes>
    </div>
  );
}

export default App;
