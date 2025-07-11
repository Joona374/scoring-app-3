import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home/Home";
import Login from "./pages/Login/Login";
import Register from "./pages/Register/Register";
import TeamDashboard from "./pages/Dashboard/Dashboard";
import ProtectRoute from "./routing/ProtectedRoute";
import Navbar from "./components/navbar/Navbar";
import CreateTeam from "./pages/CreateTeam/CreateTeam";
import Tagging from "./pages/Tagging/Tagging";
import AdminPage from "./pages/Admin/AdminPage";
import CreateGame from "./pages/CreateGame/CreateGame";
import ExcelTest from "./pages/ExcelTest/ExcelTest";
import RosterManagement from "./pages/RosterManagement/RosterManagement";

function App() {
  return (
    <div
      className="app-container"
      style={{ display: "flex", flexDirection: "column", height: "100%" }}
    >
      <Navbar></Navbar>
      <div className="routes-container" style={{ flex: 1, overflow: "hidden" }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={
              <ProtectRoute>
                <TeamDashboard />
              </ProtectRoute>
            }
          />
          <Route
            path="/create-team"
            element={
              <ProtectRoute>
                <CreateTeam />
              </ProtectRoute>
            }
          />
          <Route
            path="/roster-management"
            element={
              <ProtectRoute>
                <RosterManagement />
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
          <Route
            path="/create-game"
            element={
              <ProtectRoute>
                <CreateGame />
              </ProtectRoute>
            }
          />
          <Route
            path="/excel-test"
            element={
              <ProtectRoute>
                <ExcelTest />
              </ProtectRoute>
            }
          />
          {/* TODO: PROTECT THIS IN PROD */}
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
