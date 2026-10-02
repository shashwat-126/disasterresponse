import React from "react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getActionReports } from "../api/actionReports";
import { getDepartments } from "../api/departments";
import SeverityBadge from "../components/SeverityBadge";
import { fileNameOf, fileUrl, isImagePath, isVideoPath } from "../utils/fileUrl";

const DISASTER_TYPES = ["FLOOD", "EARTHQUAKE", "CYCLONE", "WILDFIRE", "LANDSLIDE", "STORM", "DROUGHT", "INDUSTRIAL_FIRE"];

function ProofFiles({ paths }) {
  if (!paths || paths.length === 0) {
    return <span className="eyebrow" style={{ color: "var(--text-muted)" }}>No files attached</span>;
  }
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
      {paths.map((path, i) => {
        const url = fileUrl(path);
        if (isImagePath(path)) {
          return (
            <a key={i} href={url} target="_blank" rel="noreferrer" title={fileNameOf(path)}>
              <img src={url} alt="proof" style={{ width: 56, height: 56, objectFit: "cover", borderRadius: 8, border: "1px solid var(--border)" }} />
            </a>
          );
        }
        return (
          <a key={i} href={url} target="_blank" rel="noreferrer" className="btn btn-sm" style={{ textDecoration: "none" }}>
            {isVideoPath(path) ? "▶ " : "▤ "}
            {fileNameOf(path)}
          </a>
        );
      })}
    </div>
  );
}

export default function AdminActionReports() {
  const [reports, setReports] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [departmentId, setDepartmentId] = useState("");
  const [disasterType, setDisasterType] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getDepartments().then(setDepartments).catch(() => setDepartments([]));
  }, []);

  useEffect(() => {
    setLoading(true);
    getActionReports({ departmentId: departmentId || undefined, disasterType: disasterType || undefined })
      .then((data) => {
        setReports(data);
        setError("");
      })
      .catch((err) => setError(err?.response?.data?.detail || "Could not load action reports"))
      .finally(() => setLoading(false));
  }, [departmentId, disasterType]);

  const totalProofFiles = reports.reduce((sum, r) => sum + (r.proof_file_paths?.length || 0), 0);

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Action reports</h1>
          <p className="page-subtitle">
            Every completion report and proof file filed by every department, across every incident —
            for audit and after-action review without opening each incident individually.
          </p>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 16 }}>
        <div className="stat-card">
          <div className="stat-card-label">Reports on file</div>
          <div className="stat-card-value mono">{reports.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">Proof files attached</div>
          <div className="stat-card-value mono">{totalProofFiles}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">Departments reporting</div>
          <div className="stat-card-value mono">{new Set(reports.map((r) => r.department.id)).size}</div>
        </div>
      </div>

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        <select value={departmentId} onChange={(e) => setDepartmentId(e.target.value)} style={{ maxWidth: 260 }}>
          <option value="">All departments</option>
          {departments.map((d) => (
            <option key={d.id} value={d.id}>{d.name}</option>
          ))}
        </select>
        <select value={disasterType} onChange={(e) => setDisasterType(e.target.value)} style={{ maxWidth: 220 }}>
          <option value="">All disaster types</option>
          {DISASTER_TYPES.map((t) => (
            <option key={t} value={t}>{t.replace("_", " ")}</option>
          ))}
        </select>
      </div>

      {error ? <div className="banner banner-danger">{error}</div> : null}

      <div style={{ display: "grid", gap: 12 }}>
        {loading ? (
          <div className="empty-state">Loading...</div>
        ) : reports.length === 0 ? (
          <div className="empty-state">No action reports match this filter.</div>
        ) : (
          reports.map((report) => (
            <div key={report.id} className="card card-sm">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12, flexWrap: "wrap" }}>
                <div>
                  <Link to={`/incidents/${report.incident_id}`} className="link" style={{ fontWeight: 700, fontSize: 15 }}>
                    {report.incident_title}
                  </Link>
                  <div className="eyebrow" style={{ marginTop: 4 }}>
                    {report.department.name} · {report.incident_location} · {report.disaster_type}
                  </div>
                </div>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <SeverityBadge severity={report.severity} />
                  <span className="mono" style={{ fontSize: 12, color: "var(--text-muted)" }}>
                    {new Date(report.created_at).toLocaleString()}
                  </span>
                </div>
              </div>

              <div style={{ marginTop: 12, fontSize: 14, color: "var(--text-secondary)", display: "grid", gap: 4 }}>
                <div><strong style={{ color: "var(--text-primary)" }}>Officer:</strong> {report.officer_name}</div>
                {report.team_members ? <div><strong style={{ color: "var(--text-primary)" }}>Team:</strong> {report.team_members}</div> : null}
                {report.resources_used ? <div><strong style={{ color: "var(--text-primary)" }}>Resources used:</strong> {report.resources_used}</div> : null}
                <div><strong style={{ color: "var(--text-primary)" }}>Action taken:</strong> {report.action_taken}</div>
                {report.remarks ? <div><strong style={{ color: "var(--text-primary)" }}>Remarks:</strong> {report.remarks}</div> : null}
              </div>

              <div style={{ marginTop: 12 }}>
                <div className="eyebrow" style={{ marginBottom: 6 }}>Proof files</div>
                <ProofFiles paths={report.proof_file_paths} />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
