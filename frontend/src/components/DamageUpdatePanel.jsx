import React from "react";
import { useState } from "react";
import { createDamageUpdate } from "../api/damageUpdates";
import { useAuth } from "../context/AuthContext";

export default function DamageUpdatePanel({ incident, onChange }) {
  const { user } = useAuth();
  const [showForm, setShowForm] = useState(false);
  const [description, setDescription] = useState("");
  const [revisedPeopleAffected, setRevisedPeopleAffected] = useState("");
  const [revisedInjuries, setRevisedInjuries] = useState("");
  const [severityReassessment, setSeverityReassessment] = useState("");
  const [departmentId, setDepartmentId] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const isDepartmentStaff = user?.role === "DEPARTMENT_STAFF";
  const isAdmin = user?.role === "ADMIN";
  const assignedDepartments = (incident.assignments || []).map((a) => a.department);
  const staffIsAssigned = isDepartmentStaff && assignedDepartments.some((d) => d.id === user.department_id);
  const canPost = staffIsAssigned || isAdmin;

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await createDamageUpdate(incident.id, {
        description,
        revisedPeopleAffected,
        revisedInjuries,
        severityReassessment,
        departmentId: isAdmin ? departmentId : undefined,
      });
      setDescription("");
      setRevisedPeopleAffected("");
      setRevisedInjuries("");
      setSeverityReassessment("");
      setShowForm(false);
      onChange?.();
    } catch (err) {
      setError(err?.response?.data?.detail || "Could not post damage update");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3 style={{ fontSize: 16 }}>Damage assessment updates</h3>
        {canPost ? (
          <button onClick={() => setShowForm((v) => !v)} className="btn btn-sm">
            {showForm ? "Cancel" : "Post update"}
          </button>
        ) : null}
      </div>

      {error ? <div className="banner banner-danger" style={{ marginTop: 10 }}>{error}</div> : null}

      {showForm ? (
        <form onSubmit={handleSubmit} style={{ display: "grid", gap: 10, marginTop: 14 }}>
          {isAdmin ? (
            <select value={departmentId} onChange={(e) => setDepartmentId(e.target.value)} required>
              <option value="">Posting on behalf of department...</option>
              {assignedDepartments.map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          ) : null}
          <textarea
            placeholder="What's changed on the ground since the last report?"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            rows={3}
          />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10 }}>
            <input
              type="number"
              min="0"
              placeholder="Revised people affected"
              value={revisedPeopleAffected}
              onChange={(e) => setRevisedPeopleAffected(e.target.value)}
            />
            <input
              type="number"
              min="0"
              placeholder="Revised injuries"
              value={revisedInjuries}
              onChange={(e) => setRevisedInjuries(e.target.value)}
            />
            <select value={severityReassessment} onChange={(e) => setSeverityReassessment(e.target.value)}>
              <option value="">No severity change</option>
              <option value="LOW">LOW</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="HIGH">HIGH</option>
              <option value="CRITICAL">CRITICAL</option>
            </select>
          </div>
          <button type="submit" disabled={saving} className="btn btn-primary" style={{ justifySelf: "start" }}>
            {saving ? "Posting..." : "Post damage update"}
          </button>
        </form>
      ) : null}

      <div style={{ display: "grid", gap: 10, marginTop: 16 }}>
        {(incident.damage_updates || []).length === 0 ? (
          <div className="empty-state">No damage updates posted yet.</div>
        ) : (
          incident.damage_updates.map((update) => (
            <div key={update.id} className="card-sm" style={{ background: "var(--canvas)", border: "1px solid var(--border)", borderRadius: "var(--radius-md)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 700, fontSize: 14 }}>
                <span>{update.department?.name}</span>
                <span className="mono" style={{ fontWeight: 500, color: "var(--text-muted)", fontSize: 12 }}>
                  {new Date(update.created_at).toLocaleString()}
                </span>
              </div>
              <div style={{ color: "var(--text-secondary)", marginTop: 6, fontSize: 14 }}>{update.description}</div>
              <div className="eyebrow" style={{ marginTop: 8 }}>
                {update.revised_people_affected != null ? `Revised affected: ${update.revised_people_affected}  ` : ""}
                {update.revised_injuries != null ? `Revised injuries: ${update.revised_injuries}  ` : ""}
                {update.severity_reassessment ? `Suggested severity: ${update.severity_reassessment}` : ""}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
