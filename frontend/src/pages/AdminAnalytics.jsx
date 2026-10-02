import React from "react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getAuditLogs,
  getDepartmentPerformance,
  getDistribution,
  getSlaOverview,
  getTrend,
} from "../api/analytics";
import { downloadIncidentsCsv } from "../api/exports";
import BarChart from "../components/BarChart";
import TrendChart from "../components/TrendChart";

const severityColorMap = { LOW: "#1d4ed8", MEDIUM: "#b45309", HIGH: "#b91c1c", CRITICAL: "#6d28d9" };
const priorityColorMap = { P1: "#b91c1c", P2: "#c2410c", P3: "#b45309", P4: "#1d4ed8" };

function Panel({ title, children, action }) {
  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h3 style={{ fontSize: 16 }}>{title}</h3>
        {action}
      </div>
      {children}
    </div>
  );
}

export default function AdminAnalytics() {
  const [distribution, setDistribution] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [sla, setSla] = useState(null);
  const [trend, setTrend] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [error, setError] = useState("");
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    Promise.all([getDistribution(), getDepartmentPerformance(), getSlaOverview(), getTrend(30), getAuditLogs({ limit: 25 })])
      .then(([d, dept, s, t, logs]) => {
        setDistribution(d);
        setDepartments(dept);
        setSla(s);
        setTrend(t);
        setAuditLogs(logs);
      })
      .catch((err) => setError(err?.response?.data?.detail || "Could not load analytics. Admin access required."));
  }, []);

  async function handleExport() {
    setExporting(true);
    try {
      await downloadIncidentsCsv();
    } finally {
      setExporting(false);
    }
  }

  if (error) return <div className="banner banner-danger">{error}</div>;
  if (!distribution) return <div className="empty-state">Loading analytics...</div>;

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Analytics &amp; oversight</h1>
          <p className="page-subtitle">Operational picture across severity, departments, SLA compliance, and audit trail.</p>
        </div>
        <button onClick={handleExport} disabled={exporting} className="btn btn-primary">
          {exporting ? "Exporting..." : "Export incidents CSV"}
        </button>
      </div>

      <section style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 20 }}>
        <Panel title="By severity">
          <BarChart data={distribution.severity} colorMap={severityColorMap} />
        </Panel>
        <Panel title="By status">
          <BarChart data={distribution.status} />
        </Panel>
        <Panel title="By priority">
          <BarChart data={distribution.priority} colorMap={priorityColorMap} />
        </Panel>
      </section>

      <Panel title={`Incident volume — last ${trend.days} days`}>
        <TrendChart series={trend.series} />
      </Panel>

      <Panel title={`SLA breaches (${sla.breached_count} of ${sla.open_incidents} open incidents)`}>
        {sla.breached_incidents.length === 0 ? (
          <div style={{ color: "#15803d", fontSize: 14 }}>No SLA breaches — all open incidents are within target response time.</div>
        ) : (
          <div style={{ display: "grid", gap: 10 }}>
            {sla.breached_incidents.map((inc) => (
              <div key={inc.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: 12, background: "var(--danger-soft)", borderRadius: "var(--radius-md)", border: "1px solid #f5c6c2" }}>
                <div>
                  <Link to={`/incidents/${inc.id}`} className="link" style={{ fontWeight: 700 }}>{inc.title}</Link>
                  <div className="eyebrow" style={{ marginTop: 2 }}>{inc.severity} · {inc.status} · target {inc.sla_target_minutes} min</div>
                </div>
                <div className="mono" style={{ color: "var(--danger)", fontWeight: 700, fontSize: 13.5 }}>+{inc.minutes_overdue} min overdue</div>
              </div>
            ))}
          </div>
        )}
      </Panel>

      <Panel title="Department performance">
        <div style={{ overflowX: "auto" }}>
          <table className="table">
            <thead>
              <tr>
                <th>Department</th>
                <th>Assigned</th>
                <th>Completed</th>
                <th>Pending</th>
                <th>Completion rate</th>
                <th>Avg. completion (min)</th>
              </tr>
            </thead>
            <tbody>
              {departments.map((d) => (
                <tr key={d.department_id}>
                  <td style={{ fontWeight: 600 }}>{d.name}</td>
                  <td className="mono">{d.total_assigned}</td>
                  <td className="mono">{d.completed}</td>
                  <td className="mono">{d.pending}</td>
                  <td className="mono">{d.completion_rate}%</td>
                  <td className="mono">{d.avg_completion_minutes ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      <Panel title="Recent audit log">
        <div style={{ overflowX: "auto" }}>
          <table className="table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Action</th>
                <th>Entity</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.map((log) => (
                <tr key={log.id}>
                  <td className="mono" style={{ color: "var(--text-muted)" }}>{new Date(log.created_at).toLocaleString()}</td>
                  <td style={{ fontWeight: 600 }}>{log.action}</td>
                  <td className="mono">{log.entity_type} #{log.entity_id}</td>
                  <td style={{ color: "var(--text-secondary)" }}>{log.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}
