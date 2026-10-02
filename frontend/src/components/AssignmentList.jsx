import React from "react";
import { useState } from "react";
import { acknowledgeAssignment, startAssignment } from "../api/assignments";
import { useAuth } from "../context/AuthContext";
import { fileNameOf, fileUrl, isImagePath, isVideoPath } from "../utils/fileUrl";
import ActionReportForm from "./ActionReportForm";
import AssignmentStatusBadge from "./AssignmentStatusBadge";

function ProofFiles({ paths }) {
  if (!paths || paths.length === 0) return null;
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 10 }}>
      {paths.map((path, i) => {
        const url = fileUrl(path);
        if (isImagePath(path)) {
          return (
            <a key={i} href={url} target="_blank" rel="noreferrer" title={fileNameOf(path)}>
              <img
                src={url}
                alt="proof"
                style={{ width: 72, height: 72, objectFit: "cover", borderRadius: 10, border: "1px solid var(--border)" }}
              />
            </a>
          );
        }
        return (
          <a
            key={i}
            href={url}
            target="_blank"
            rel="noreferrer"
            className="btn btn-sm"
            style={{ textDecoration: "none" }}
          >
            {isVideoPath(path) ? "▶ " : "▤ "}
            {fileNameOf(path)}
          </a>
        );
      })}
    </div>
  );
}

export default function AssignmentList({ assignments, onChange }) {
  const { user } = useAuth();
  const [activeFormId, setActiveFormId] = useState(null);
  const [busyId, setBusyId] = useState(null);

  function canAct(assignment) {
    if (!user) return false;
    if (user.role === "ADMIN") return true;
    return user.role === "DEPARTMENT_STAFF" && user.department_id === assignment.department.id;
  }

  async function handleAcknowledge(assignment) {
    setBusyId(assignment.id);
    try {
      await acknowledgeAssignment(assignment.id);
      onChange?.();
    } finally {
      setBusyId(null);
    }
  }

  async function handleStart(assignment) {
    setBusyId(assignment.id);
    try {
      await startAssignment(assignment.id);
      onChange?.();
    } finally {
      setBusyId(null);
    }
  }

  if (!assignments || assignments.length === 0) {
    return <div className="empty-state">No departments assigned yet.</div>;
  }

  return (
    <div style={{ display: "grid", gap: 12 }}>
      {assignments.map((assignment) => (
        <div key={assignment.id} className="card card-sm">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
            <div>
              <div style={{ fontWeight: 700 }}>
                {assignment.department.name}
                {assignment.is_lead ? <span style={{ color: "var(--accent)", fontWeight: 600 }}> · Lead</span> : null}
              </div>
              <div className="eyebrow" style={{ marginTop: 2 }}>{assignment.department.category.replace("_", " ")}</div>
            </div>
            <AssignmentStatusBadge status={assignment.status} />
          </div>

          {assignment.action_report ? (
            <div style={{ marginTop: 12, background: "var(--canvas)", borderRadius: 12, padding: 12, fontSize: 14, color: "var(--text-secondary)" }}>
              <div><strong style={{ color: "var(--text-primary)" }}>Officer:</strong> {assignment.action_report.officer_name}</div>
              {assignment.action_report.team_members ? (
                <div><strong style={{ color: "var(--text-primary)" }}>Team:</strong> {assignment.action_report.team_members}</div>
              ) : null}
              {assignment.action_report.resources_used ? (
                <div><strong style={{ color: "var(--text-primary)" }}>Resources used:</strong> {assignment.action_report.resources_used}</div>
              ) : null}
              <div><strong style={{ color: "var(--text-primary)" }}>Action taken:</strong> {assignment.action_report.action_taken}</div>
              {assignment.action_report.remarks ? <div><strong style={{ color: "var(--text-primary)" }}>Remarks:</strong> {assignment.action_report.remarks}</div> : null}
              <div className="mono" style={{ marginTop: 6, fontSize: 12, color: "var(--text-muted)" }}>
                Filed {new Date(assignment.action_report.created_at).toLocaleString()}
              </div>
              {assignment.action_report.proof_file_paths?.length > 0 ? (
                <>
                  <div style={{ fontWeight: 700, color: "var(--text-primary)", marginTop: 10 }}>
                    Proof files ({assignment.action_report.proof_file_paths.length})
                  </div>
                  <ProofFiles paths={assignment.action_report.proof_file_paths} />
                </>
              ) : null}
            </div>
          ) : canAct(assignment) ? (
            <div style={{ display: "flex", gap: 10, marginTop: 12 }}>
              {assignment.status === "ASSIGNED" ? (
                <button onClick={() => handleAcknowledge(assignment)} disabled={busyId === assignment.id} className="btn btn-sm">
                  Acknowledge
                </button>
              ) : null}
              {(assignment.status === "ASSIGNED" || assignment.status === "ACKNOWLEDGED") ? (
                <button onClick={() => handleStart(assignment)} disabled={busyId === assignment.id} className="btn btn-sm">
                  Start work
                </button>
              ) : null}
              <button onClick={() => setActiveFormId(assignment.id)} className="btn btn-primary btn-sm">
                Submit action report
              </button>
            </div>
          ) : (
            <div className="empty-state" style={{ marginTop: 12, padding: 10 }}>Awaiting this department's action report.</div>
          )}

          {activeFormId === assignment.id ? (
            <div style={{ marginTop: 16 }}>
              <ActionReportForm
                assignmentId={assignment.id}
                onCancel={() => setActiveFormId(null)}
                onSubmitted={() => {
                  setActiveFormId(null);
                  onChange?.();
                }}
              />
            </div>
          ) : null}
        </div>
      ))}
    </div>
  );
}
