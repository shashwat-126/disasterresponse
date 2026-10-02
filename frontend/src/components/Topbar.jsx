import React from "react";
import { useLocation } from "react-router-dom";
import NotificationBell from "./NotificationBell";

const TITLES = [
  { match: /^\/$/, eyebrow: "Command overview", title: "Overview" },
  { match: /^\/incidents$/, eyebrow: "Operations", title: "Incident queue" },
  { match: /^\/incidents\/\d+$/, eyebrow: "Operations", title: "Incident detail" },
  { match: /^\/submit$/, eyebrow: "Intake", title: "Submit incident" },
  { match: /^\/department-dashboard$/, eyebrow: "Department", title: "Department queue" },
  { match: /^\/analytics$/, eyebrow: "Oversight", title: "Analytics & oversight" },
  { match: /^\/action-reports$/, eyebrow: "Oversight", title: "Action reports" },
];

export default function Topbar() {
  const location = useLocation();
  const entry = TITLES.find((t) => t.match.test(location.pathname)) || { eyebrow: "EADRP", title: "Console" };

  return (
    <div className="topbar">
      <div>
        <div className="eyebrow">{entry.eyebrow}</div>
        <div className="topbar-title">{entry.title}</div>
      </div>
      <div style={{ marginLeft: "auto" }}>
        <NotificationBell />
      </div>
    </div>
  );
}
