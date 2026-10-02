import React from "react";
import { useState } from "react";
import { createResourceRequest, resolveResourceRequest } from "../api/resourceRequests";
import { resourceRequestColors } from "../utils/constants";
import { useAuth } from "../context/AuthContext";

function StatusPill({ status }) {
  const palette = resourceRequestColors[status] || { bg: "#e5e7eb", text: "#374151" };
  return (
    <span className="badge" style={{ backgroundColor: palette.bg, color: palette.text }}>
      {status}
    </span>
  );
}

export default function ResourceRequestPanel({ incident, onChange }) {
  const { user } = useAuth();
  const [showForm, setShowForm] = useState(false);
  const [resourceType, setResourceType] = useState("");
  const [quantity, setQuantity] = useState("");
  const [justification, setJustification] = useState("");
  const [departmentId, setDepartmentId] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [busyId, setBusyId] = useState(null);

  const isDepartmentStaff = user?.role === "DEPARTMENT_STAFF";
  const isAdmin = user?.role === "ADMIN";
  const assignedDepartments = (incident.assignments || []).map((a) => a.department);
  const staffIsAssigned = isDepartmentStaff && assignedDepartments.some((d) => d.id === user.department_id);
  const canRequest = staffIsAssigned || isAdmin;

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await createResourceRequest(incident.id, {
        resourceType,
        quantity,
        justification,
        departmentId: isAdmin ? departmentId : undefined,
      });
      setResourceType("");
      setQuantity("");
      setJustification("");
      setShowForm(false);
      onChange?.();
    } catch (err) {
      setError(err?.response?.data?.detail || "Could not submit resource request");
    } finally {
      setSaving(false);
    }
  }

  async function handleResolve(requestId, status) {
    setBusyId(requestId);
    try {
      await resolveResourceRequest(requestId, status);
      onChange?.();
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3 style={{ fontSize: 16 }}>Resource requests</h3>
        {canRequest ? (
          <button onClick={() => setShowForm((v) => !v)} className="btn btn-sm">
            {showForm ? "Cancel" : "Request more"}
          </button>
        ) : null}
      </div>

      {error ? <div className="banner banner-danger" style={{ marginTop: 10 }}>{error}</div> : null}

      {showForm ? (
        <form onSubmit={handleSubmit} style={{ display: "grid", gap: 10, marginTop: 14 }}>
          {isAdmin ? (
            <select value={departmentId} onChange={(e) => setDepartmentId(e.target.value)} required>
              <option value="">Requesting on behalf of department...</option>
              {assignedDepartments.map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          ) : null}
          <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 10 }}>
            <input
              placeholder="Resource type (e.g. ambulances, boats, food kits)"
              value={resourceType}
              onChange={(e) => setResourceType(e.target.value)}
              required
            />
            <input
              type="number"
              min="1"
              placeholder="Quantity"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              required
            />
          </div>
          <textarea
            placeholder="Why is this needed beyond what was already allocated?"
            value={justification}
            onChange={(e) => setJustification(e.target.value)}
            required
            rows={2}
          />
          <button type="submit" disabled={saving} className="btn btn-primary" style={{ justifySelf: "start" }}>
            {saving ? "Submitting..." : "Submit request"}
          </button>
        </form>
      ) : null}

      <div style={{ display: "grid", gap: 10, marginTop: 16 }}>
        {(incident.resource_requests || []).length === 0 ? (
          <div className="empty-state">No extra resource requests for this incident.</div>
        ) : (
          incident.resource_requests.map((request) => (
            <div key={request.id} className="card-sm" style={{ background: "var(--canvas)", border: "1px solid var(--border)", borderRadius: "var(--radius-md)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ fontWeight: 700, fontSize: 14 }}>
                  {request.department?.name} · <span className="mono">{request.quantity} × {request.resource_type}</span>
                </div>
                <StatusPill status={request.status} />
              </div>
              <div style={{ color: "var(--text-secondary)", marginTop: 6, fontSize: 14 }}>{request.justification}</div>
              {request.resolution_notes ? (
                <div className="eyebrow" style={{ marginTop: 6 }}>Note: {request.resolution_notes}</div>
              ) : null}
              {isAdmin && request.status === "PENDING" ? (
                <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
                  <button disabled={busyId === request.id} onClick={() => handleResolve(request.id, "APPROVED")} className="btn btn-sm">
                    Approve
                  </button>
                  <button disabled={busyId === request.id} onClick={() => handleResolve(request.id, "FULFILLED")} className="btn btn-sm">
                    Mark fulfilled
                  </button>
                  <button disabled={busyId === request.id} onClick={() => handleResolve(request.id, "REJECTED")} className="btn btn-sm btn-danger">
                    Reject
                  </button>
                </div>
              ) : null}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
