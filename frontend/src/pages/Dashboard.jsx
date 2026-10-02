import React from "react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getDashboardSummary } from "../api/dashboard";
import { getIncidents } from "../api/incidents";
import SeverityBadge from "../components/SeverityBadge";

function StatCard({ label, value, sub }) {
  return (
    <div className="stat-card">
      <div className="stat-card-label">{label}</div>
      <div className="stat-card-value mono">{value}</div>
      {sub ? <div className="stat-card-sub">{sub}</div> : null}
    </div>
  );
}

function Guidance({ title, body }) {
  return (
    <div className="card-sm" style={{ background: "var(--canvas)", border: "1px solid var(--border)", borderRadius: "var(--radius-md)" }}>
      <div style={{ fontWeight: 700 }}>{title}</div>
      <div style={{ color: "var(--text-secondary)", marginTop: 6, lineHeight: 1.5, fontSize: 14 }}>{body}</div>
    </div>
  );
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getDashboardSummary(), getIncidents()])
      .then(([summaryData, incidentsData]) => {
        setSummary(summaryData);
        setIncidents(incidentsData);
      })
      .catch((err) => setError(err?.response?.data?.detail || "Could not load dashboard"));
  }, []);

  const recentIncidents = useMemo(() => incidents.slice(0, 6), [incidents]);
  const load = useMemo(() => {
    const totalAffected = incidents.reduce((acc, item) => acc + (item.people_affected || 0), 0);
    const totalInjuries = incidents.reduce((acc, item) => acc + (item.injuries || 0), 0);
    return { totalAffected, totalInjuries };
  }, [incidents]);

  if (error) return <div className="banner banner-danger">{error}</div>;
  if (!summary) return <div className="empty-state">Loading dashboard...</div>;

  return (
    <div style={{ display: "grid", gap: 24 }}>
      <div style={{ display: "flex", gap: 10 }}>
        <Link to="/submit" className="btn btn-primary">＋ Report an incident</Link>
        <Link to="/incidents" className="btn">Review full queue</Link>
      </div>

      <section style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: 16 }}>
        <StatCard label="Total incidents" value={summary.total_incidents} />
        <StatCard label="Critical" value={summary.critical_incidents} sub="Needs senior coordinator" />
        <StatCard label="High" value={summary.high_incidents} />
        <StatCard label="Resolved" value={summary.resolved_incidents} />
      </section>

      <section style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 16 }}>
        <StatCard label="People affected (open incidents)" value={load.totalAffected} />
        <StatCard label="Reported injuries (open incidents)" value={load.totalInjuries} />
      </section>

      <section style={{ display: "grid", gridTemplateColumns: "1.3fr 1fr", gap: 20 }}>
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
            <h3 style={{ fontSize: 16 }}>Recent incidents</h3>
            <Link to="/incidents" className="link" style={{ fontSize: 13.5 }}>See all →</Link>
          </div>
          <div style={{ display: "grid", gap: 12 }}>
            {recentIncidents.length === 0 ? (
              <div className="empty-state">No incidents recorded yet.</div>
            ) : (
              recentIncidents.map((incident) => (
                <Link
                  key={incident.id}
                  to={`/incidents/${incident.id}`}
                  style={{
                    display: "flex", justifyContent: "space-between", alignItems: "center", gap: 16,
                    paddingBottom: 12, borderBottom: "1px solid var(--border)", textDecoration: "none", color: "inherit",
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 14 }}>{incident.title}</div>
                    <div className="eyebrow" style={{ marginTop: 2 }}>{incident.location} · {incident.disaster_type}</div>
                  </div>
                  <SeverityBadge severity={incident.severity} />
                </Link>
              ))
            )}
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: 16, marginBottom: 14 }}>Response guidance</h3>
          <div style={{ display: "grid", gap: 12 }}>
            <Guidance title="Critical incidents" body="Escalate immediately, assign a senior coordinator, and verify shelter availability." />
            <Guidance title="High incidents" body="Validate field intel, confirm ambulance routes, and stage multi-agency resources." />
            <Guidance title="Model confidence" body="Low-confidence predictions should be reviewed manually before dispatch decisions." />
          </div>
        </div>
      </section>
    </div>
  );
}
