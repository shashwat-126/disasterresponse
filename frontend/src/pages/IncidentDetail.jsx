import React from "react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getIncident, updateIncidentStatus } from "../api/incidents";
import { getAttachments } from "../api/attachments";
import { downloadIncidentReport } from "../api/exports";
import AdminCoordinationPanel from "../components/AdminCoordinationPanel";
import AssignmentList from "../components/AssignmentList";
import DamageUpdatePanel from "../components/DamageUpdatePanel";
import ResourceRequestPanel from "../components/ResourceRequestPanel";
import SeverityBadge from "../components/SeverityBadge";
import { useAuth } from "../context/AuthContext";
import { fileUrl } from "../utils/fileUrl";
import { priorityColors } from "../utils/constants";

function Metric({ label, value }) {
  return (
    <div className="stat-card">
      <div className="stat-card-label">{label}</div>
      <div className="stat-card-value mono" style={{ fontSize: 22 }}>{value}</div>
    </div>
  );
}

function PriorityBadge({ priority }) {
  const palette = priorityColors[priority] || { bg: "#e5e7eb", text: "#374151" };
  return (
    <span className="badge" style={{ backgroundColor: palette.bg, color: palette.text }}>
      {priority}
    </span>
  );
}

export default function IncidentDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [incident, setIncident] = useState(null);
  const [attachments, setAttachments] = useState([]);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [resolveError, setResolveError] = useState("");
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    load();
  }, [id]);

  async function load() {
    try {
      const data = await getIncident(id);
      setIncident(data);
      try {
        const files = await getAttachments(id);
        setAttachments(files);
      } catch {
        setAttachments([]);
      }
    } catch (err) {
      setError(err?.response?.data?.detail || "Could not load incident");
    }
  }

  async function markResolved() {
    setSaving(true);
    setResolveError("");
    try {
      await updateIncidentStatus(id, "RESOLVED");
      await load();
    } catch (err) {
      setResolveError(err?.response?.data?.detail || "Could not resolve incident");
    } finally {
      setSaving(false);
    }
  }

  async function handleDownloadReport() {
    setDownloading(true);
    try {
      await downloadIncidentReport(id);
    } finally {
      setDownloading(false);
    }
  }

  if (error) return <div className="banner banner-danger">{error}</div>;
  if (!incident) return <div className="empty-state">Loading incident...</div>;

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <div className="page-header">
        <div>
          <div className="eyebrow" style={{ marginBottom: 6 }}>Incident #{incident.id}</div>
          <h1 className="page-title" style={{ marginBottom: 4 }}>{incident.title}</h1>
          <div style={{ color: "var(--text-secondary)" }}>{incident.location} · {incident.disaster_type}</div>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
          <SeverityBadge severity={incident.severity} />
          <PriorityBadge priority={incident.priority_level} />
          {incident.sla_breached ? <span className="badge" style={{ backgroundColor: "var(--danger-soft)", color: "var(--danger)" }}>SLA BREACHED</span> : null}
          <button onClick={handleDownloadReport} disabled={downloading} className="btn">
            {downloading ? "Preparing..." : "Download PDF report"}
          </button>
          <button
            onClick={markResolved}
            disabled={saving || incident.status === "RESOLVED" || !incident.ready_to_resolve}
            title={!incident.ready_to_resolve ? "All assigned departments must submit action reports first" : ""}
            className="btn btn-primary"
          >
            {incident.status === "RESOLVED" ? "Resolved" : saving ? "Saving..." : "Mark resolved"}
          </button>
        </div>
      </div>

      {resolveError ? <div className="banner banner-danger">{resolveError}</div> : null}

      {incident.possible_duplicate_of ? (
        <div className="banner banner-warning">
          This report may be a duplicate of{" "}
          <Link to={`/incidents/${incident.possible_duplicate_of}`} style={{ color: "#92400e", fontWeight: 700 }}>
            incident #{incident.possible_duplicate_of}
          </Link>{" "}
          — same disaster type reported nearby within the last few hours. Review before dispatching duplicate resources.
        </div>
      ) : null}

      <div className="card">
        <p style={{ margin: 0, lineHeight: 1.7 }}>{incident.description}</p>
        {incident.additional_info ? (
          <>
            <div className="eyebrow" style={{ marginTop: 16, marginBottom: 6 }}>Other information from reporter</div>
            <p style={{ margin: 0, color: "var(--text-secondary)", lineHeight: 1.7 }}>{incident.additional_info}</p>
          </>
        ) : null}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, minmax(0, 1fr))", gap: 16 }}>
        <Metric label="Status" value={incident.status} />
        <Metric label="Risk score" value={`${incident.risk_score}/100`} />
        <Metric label="Est. response" value={`${incident.estimated_response_minutes} min`} />
        <Metric label="People affected" value={incident.people_affected} />
        <Metric label="Injuries" value={incident.injuries} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <div className="card">
          <h3 style={{ fontSize: 16 }}>AI assessment</h3>
          <div style={{ color: "var(--text-secondary)", lineHeight: 1.8, marginBottom: 12, fontSize: 14 }}>
            <div><strong style={{ color: "var(--text-primary)" }}>Model version:</strong> <span className="mono">{incident.model_version}</span></div>
            <div><strong style={{ color: "var(--text-primary)" }}>Confidence:</strong> <span className="mono">{Math.round((incident.prediction_confidence || 0) * 100)}%</span></div>
            <div><strong style={{ color: "var(--text-primary)" }}>Why:</strong> {incident.explanation_summary || "—"}</div>
          </div>
          {incident.secondary_hazards?.length > 0 ? (
            <div style={{ marginBottom: 12 }}>
              <div className="eyebrow" style={{ marginBottom: 4 }}>Secondary hazards</div>
              <ul style={{ margin: 0, paddingLeft: 20, color: "var(--text-secondary)", fontSize: 14 }}>
                {incident.secondary_hazards.map((h, i) => <li key={i}>{h}</li>)}
              </ul>
            </div>
          ) : null}
          {incident.immediate_recommendations?.length > 0 ? (
            <div>
              <div className="eyebrow" style={{ marginBottom: 4 }}>Immediate recommendations</div>
              <ul style={{ margin: 0, paddingLeft: 20, color: "var(--text-secondary)", fontSize: 14 }}>
                {incident.immediate_recommendations.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          ) : null}
        </div>

        <div className="card">
          <h3 style={{ fontSize: 16 }}>Recommended allocation</h3>
          {incident.allocation ? (
            <div style={{ color: "var(--text-secondary)", lineHeight: 1.8, fontSize: 14 }} className="mono">
              <div><strong style={{ color: "var(--text-primary)", fontFamily: "var(--font-sans)" }}>Ambulances:</strong> {incident.allocation.ambulances}</div>
              <div><strong style={{ color: "var(--text-primary)", fontFamily: "var(--font-sans)" }}>Rescue teams:</strong> {incident.allocation.rescue_teams}</div>
              <div><strong style={{ color: "var(--text-primary)", fontFamily: "var(--font-sans)" }}>Vehicles:</strong> {incident.allocation.vehicles}</div>
              <div><strong style={{ color: "var(--text-primary)", fontFamily: "var(--font-sans)" }}>Food kits:</strong> {incident.allocation.food_kits}</div>
              <div><strong style={{ color: "var(--text-primary)", fontFamily: "var(--font-sans)" }}>Water (liters):</strong> {incident.allocation.water_liters}</div>
              <div><strong style={{ color: "var(--text-primary)", fontFamily: "var(--font-sans)" }}>Shelters:</strong> {incident.allocation.shelters}</div>
              <div style={{ marginTop: 8, fontFamily: "var(--font-sans)" }}><strong style={{ color: "var(--text-primary)" }}>Notes:</strong> {incident.allocation.notes}</div>
            </div>
          ) : <div className="empty-state">No allocation recorded.</div>}
        </div>
      </div>

      {attachments.length > 0 ? (
        <div className="card">
          <h3 style={{ fontSize: 16 }}>Citizen-submitted media</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
            {attachments.map((a) => (
              <a key={a.id} href={fileUrl(a.file_path)} target="_blank" rel="noreferrer" style={{ display: "block" }}>
                {a.file_type === "image" ? (
                  <img src={fileUrl(a.file_path)} alt="attachment" style={{ width: 140, height: 140, objectFit: "cover", borderRadius: 12, border: "1px solid var(--border)" }} />
                ) : (
                  <div style={{ width: 140, height: 140, borderRadius: 12, border: "1px solid var(--border)", display: "grid", placeItems: "center", background: "var(--canvas)", color: "var(--text-secondary)", fontSize: 13 }}>
                    {a.file_type.toUpperCase()}
                  </div>
                )}
              </a>
            ))}
          </div>
        </div>
      ) : null}

      <div className="card">
        <h3 style={{ fontSize: 16 }}>Department response status</h3>
        <div style={{ marginTop: 12 }}>
          <AssignmentList assignments={incident.assignments} onChange={load} />
        </div>
      </div>

      <DamageUpdatePanel incident={incident} onChange={load} />
      <ResourceRequestPanel incident={incident} onChange={load} />
      {user?.role === "ADMIN" ? <AdminCoordinationPanel incident={incident} onChange={load} /> : null}
    </div>
  );
}
