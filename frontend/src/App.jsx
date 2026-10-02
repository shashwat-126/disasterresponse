import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import { AuthProvider, useAuth } from "./context/AuthContext";
import AdminActionReports from "./pages/AdminActionReports";
import AdminAnalytics from "./pages/AdminAnalytics";
import Dashboard from "./pages/Dashboard";
import DepartmentDashboard from "./pages/DepartmentDashboard";
import IncidentDetail from "./pages/IncidentDetail";
import IncidentList from "./pages/IncidentList";
import Login from "./pages/Login";
import SubmitIncident from "./pages/SubmitIncident";

function Protected({ children, roles }) {
  const { user, ready } = useAuth();
  if (!ready) return <p style={{ padding: 24 }}>Loading...</p>;
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />;
  return children;
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <BrowserRouter>
      {!user ? (
        <Routes>
          <Route path="*" element={<Login />} />
        </Routes>
      ) : (
        <div className="app-shell">
          <Sidebar />
          <div>
            <Topbar />
            <main className="content">
              <Routes>
                <Route path="/login" element={<Navigate to="/" replace />} />
                <Route path="/" element={<Dashboard />} />
                <Route path="/incidents" element={<IncidentList />} />
                <Route path="/incidents/:id" element={<IncidentDetail />} />
                <Route path="/submit" element={<SubmitIncident />} />
                <Route
                  path="/department-dashboard"
                  element={
                    <Protected roles={["DEPARTMENT_STAFF", "ADMIN"]}>
                      <DepartmentDashboard />
                    </Protected>
                  }
                />
                <Route
                  path="/analytics"
                  element={
                    <Protected roles={["ADMIN"]}>
                      <AdminAnalytics />
                    </Protected>
                  }
                />
                <Route
                  path="/action-reports"
                  element={
                    <Protected roles={["ADMIN"]}>
                      <AdminActionReports />
                    </Protected>
                  }
                />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
          </div>
        </div>
      )}
    </BrowserRouter>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
