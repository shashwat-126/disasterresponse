import React from "react";
import { Link } from "react-router-dom";
import SeverityBadge from "./SeverityBadge";

export default function IncidentCard({ incident }) {
  return (
    <Link to={`/incidents/${incident.id}`} className="card card-sm card-hover" style={{ display: "block", textDecoration: "none", color: "inherit" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16 }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: 16 }}>{incident.title}</div>
          <div className="eyebrow" style={{ marginTop: 4 }}>{incident.location} · {incident.disaster_type}</div>
        </div>
        <SeverityBadge severity={incident.severity} />
      </div>
      <div style={{ display: "flex", gap: 18, flexWrap: "wrap", marginTop: 14, color: "var(--text-secondary)", fontSize: 13.5 }}>
        <span>Status: <strong className="mono" style={{ color: "var(--text-primary)" }}>{incident.status}</strong></span>
        <span>Affected: <strong className="mono" style={{ color: "var(--text-primary)" }}>{incident.people_affected}</strong></span>
        <span>Injuries: <strong className="mono" style={{ color: "var(--text-primary)" }}>{incident.injuries}</strong></span>
        <span>Confidence: <strong className="mono" style={{ color: "var(--text-primary)" }}>{Math.round((incident.prediction_confidence || 0) * 100)}%</strong></span>
      </div>
    </Link>
  );
}
