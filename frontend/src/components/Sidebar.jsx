import React from "react";
import { useEffect, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV_ITEMS = [
  { to: "/", label: "Overview", icon: "◆", roles: null },
  { to: "/incidents", label: "Incident queue", icon: "☰", roles: null },
  { to: "/submit", label: "Submit incident", icon: "＋", roles: null },
  { to: "/department-dashboard", label: "Department queue", icon: "⌂", roles: ["DEPARTMENT_STAFF", "ADMIN"] },
  { to: "/analytics", label: "Analytics", icon: "▤", roles: ["ADMIN"] },
  { to: "/action-reports", label: "Action reports", icon: "▦", roles: ["ADMIN"] },
];

function Clock() {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  const hh = String(now.getHours()).padStart(2, "0");
  const mm = String(now.getMinutes()).padStart(2, "0");
  const ss = String(now.getSeconds()).padStart(2, "0");
  return <span className="sidebar-live-clock mono">{hh}:{mm}:{ss}</span>;
}

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  const initials = (user.full_name || "?")
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-mark">EA</div>
        <div>
          <div className="sidebar-brand-name">EADRP</div>
          <div className="sidebar-brand-sub">Disaster Response Console</div>
        </div>
      </div>

      <div className="sidebar-live">
        <span className="sidebar-live-dot" />
        <span className="sidebar-live-text">OPERATIONAL</span>
        <Clock />
      </div>

      <div className="sidebar-section-label">Console</div>
      <nav className="sidebar-nav">
        {NAV_ITEMS.filter((item) => !item.roles || item.roles.includes(user.role)).map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) => "sidebar-navlink" + (isActive ? " active" : "")}
          >
            <span className="sidebar-navlink-icon">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-spacer" />

      <div className="sidebar-user">
        <div className="sidebar-user-avatar">{initials}</div>
        <div style={{ minWidth: 0 }}>
          <div className="sidebar-user-name">{user.full_name}</div>
          <div className="sidebar-user-role">{user.role.replace("_", " ")}</div>
        </div>
        <button
          className="sidebar-logout"
          onClick={() => {
            logout();
            navigate("/login");
          }}
        >
          Log out
        </button>
      </div>
    </aside>
  );
}
