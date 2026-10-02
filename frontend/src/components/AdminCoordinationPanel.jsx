import React from "react";
import { useEffect, useState } from "react";
import { addDepartmentToIncident, reassignAssignment, removeAssignment } from "../api/assignments";
import { getDepartments } from "../api/departments";

export default function AdminCoordinationPanel({ incident, onChange }) {
  const [departments, setDepartments] = useState([]);
  const [addDepartmentId, setAddDepartmentId] = useState("");
  const [reassignTarget, setReassignTarget] = useState({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getDepartments().then(setDepartments).catch(() => setDepartments([]));
  }, []);

  const assignedIds = new Set((incident.assignments || []).map((a) => a.department.id));
  const availableToAdd = departments.filter((d) => !assignedIds.has(d.id));

  async function handleAdd(e) {
    e.preventDefault();
    if (!addDepartmentId) return;
    setBusy(true);
    setError("");
    try {
      await addDepartmentToIncident(incident.id, addDepartmentId);
      setAddDepartmentId("");
      onChange?.();
    } catch (err) {
      setError(err?.response?.data?.detail || "Could not add department");
    } finally {
      setBusy(false);
    }
  }

  async function handleReassign(assignmentId) {
    const target = reassignTarget[assignmentId];
    if (!target) return;
    setBusy(true);
    setError("");
    try {
      await reassignAssignment(assignmentId, target);
      onChange?.();
    } catch (err) {
      setError(err?.response?.data?.detail || "Could not reassign");
    } finally {
      setBusy(false);
    }
  }

  async function handleRemove(assignmentId) {
    setBusy(true);
    setError("");
    try {
      await removeAssignment(assignmentId);
      onChange?.();
    } catch (err) {
      setError(err?.response?.data?.detail || "Could not remove department");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card" style={{ borderColor: "var(--border-strong)" }}>
      <div className="eyebrow" style={{ marginBottom: 4 }}>Admin only</div>
      <h3 style={{ fontSize: 16 }}>Coordination</h3>
      <p className="page-subtitle" style={{ marginTop: 4, marginBottom: 16 }}>
        Cover cases the auto-assignment rules can't foresee — pull in an extra department, correct a
        misrouted one, or stand one down.
      </p>

      {error ? <div className="banner banner-danger" style={{ marginBottom: 12 }}>{error}</div> : null}

      <form onSubmit={handleAdd} style={{ display: "flex", gap: 10, marginBottom: 18 }}>
        <select value={addDepartmentId} onChange={(e) => setAddDepartmentId(e.target.value)} style={{ flex: 1 }}>
          <option value="">Add a department...</option>
          {availableToAdd.map((d) => (
            <option key={d.id} value={d.id}>{d.name}</option>
          ))}
        </select>
        <button type="submit" disabled={busy || !addDepartmentId} className="btn btn-primary">
          Add
        </button>
      </form>

      <div style={{ display: "grid", gap: 10 }}>
        {(incident.assignments || []).map((assignment) => (
          <div key={assignment.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 10, borderTop: "1px solid var(--border)", paddingTop: 10, flexWrap: "wrap" }}>
            <div style={{ fontWeight: 600, fontSize: 14 }}>
              {assignment.department.name} <span className="mono" style={{ color: "var(--text-muted)", fontWeight: 400 }}>({assignment.status})</span>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <select
                value={reassignTarget[assignment.id] || ""}
                onChange={(e) => setReassignTarget((prev) => ({ ...prev, [assignment.id]: e.target.value }))}
                disabled={assignment.status === "COMPLETED"}
                style={{ width: "auto" }}
              >
                <option value="">Reassign to...</option>
                {departments
                  .filter((d) => d.id !== assignment.department.id)
                  .map((d) => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
              </select>
              <button
                onClick={() => handleReassign(assignment.id)}
                disabled={busy || assignment.status === "COMPLETED" || !reassignTarget[assignment.id]}
                className="btn btn-sm"
              >
                Reassign
              </button>
              <button
                onClick={() => handleRemove(assignment.id)}
                disabled={busy || assignment.status === "COMPLETED"}
                title={assignment.status === "COMPLETED" ? "Can't remove a department that already completed its work" : ""}
                className="btn btn-sm btn-danger"
              >
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
