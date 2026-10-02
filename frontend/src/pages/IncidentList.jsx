import React from "react";
import { useEffect, useMemo, useState } from "react";
import IncidentCard from "../components/IncidentCard";
import { getIncidents } from "../api/incidents";

export default function IncidentList() {
  const [incidents, setIncidents] = useState([]);
  const [query, setQuery] = useState("");
  const [severity, setSeverity] = useState("ALL");
  const [status, setStatus] = useState("ALL");
  const [error, setError] = useState("");

  useEffect(() => {
    getIncidents().then(setIncidents).catch((err) => setError(err?.response?.data?.detail || "Failed to load incidents"));
  }, []);

  const filtered = useMemo(() => {
    return incidents.filter((incident) => {
      const matchesQuery = [incident.title, incident.location, incident.disaster_type]
        .join(" ")
        .toLowerCase()
        .includes(query.toLowerCase());
      const matchesSeverity = severity === "ALL" || incident.severity === severity;
      const matchesStatus = status === "ALL" || incident.status === status;
      return matchesQuery && matchesSeverity && matchesStatus;
    });
  }, [incidents, query, severity, status]);

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Incident queue</h1>
          <p className="page-subtitle">Filter and review operational incidents with severity and status context.</p>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr", gap: 12 }}>
        <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search by title, location, or disaster type" />
        <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
          <option value="ALL">All severities</option>
          <option value="LOW">LOW</option>
          <option value="MEDIUM">MEDIUM</option>
          <option value="HIGH">HIGH</option>
          <option value="CRITICAL">CRITICAL</option>
        </select>
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="ALL">All statuses</option>
          <option value="SUBMITTED">SUBMITTED</option>
          <option value="RESOLVED">RESOLVED</option>
        </select>
      </div>

      {error ? <div className="banner banner-danger">{error}</div> : null}
      <div style={{ display: "grid", gap: 12 }}>
        {filtered.length === 0 ? (
          <div className="empty-state">No incidents match your filters.</div>
        ) : (
          filtered.map((incident) => <IncidentCard key={incident.id} incident={incident} />)
        )}
      </div>
    </div>
  );
}
