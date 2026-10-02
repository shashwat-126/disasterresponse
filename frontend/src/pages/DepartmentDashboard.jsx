import React from "react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { acknowledgeAssignment, startAssignment } from "../api/assignments";
import { getDepartments, getDepartmentWorkload } from "../api/departments";
import { createResourceRequest } from "../api/resourceRequests";
import SeverityBadge from "../components/SeverityBadge";
import { useAuth } from "../context/AuthContext";

const TABS = [
  { key: "pending", label: "Pending" },
  { key: "in_progress", label: "In progress" },
  { key: "completed", label: "Completed" },
];

function RequestResourceForm({ assignment, onDone, onCancel }) {
  const [resourceType, setResourceType] = useState("");
  const [quantity, setQuantity] = useState("");
  const [justification, setJustification] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await createResourceRequest(assignment.incident_id, { resourceType, quantity, justification });
      onDone();
    } catch (err) {
      setError(err?.response?.data?.detail || "Could not submit request");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form
      onClick={(e) => e.stopPropagation()}
      onSubmit={handleSubmit}
      style={{ display: "grid", gap: 8, marginTop: 12, paddingTop: 12, borderTop: "1px solid var(--border)" }}
    >
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 8 }}>
        <input
          placeholder="Resource type (e.g. boats, ambulances)"
          value={resourceType}
          onChange={(e) => setResourceType(e.target.value)}
          required
          autoFocus
        />
        <input type="number" min="1" placeholder="Qty" value={quantity} onChange={(e) => setQuantity(e.target.value)} required />
      </div>
      <textarea
        placeholder="Why is this needed beyond what's already allocated?"
        value={justification}
        onChange={(e) => setJustification(e.target.value)}
        required
        rows={2}
      />
      {error ? <div className="banner banner-danger" style={{ padding: 8, fontSize: 13 }}>{error}</div> : null}
      <div style={{ display: "flex", gap: 8 }}>
        <button type="submit" disabled={saving} className="btn btn-primary btn-sm">
          {saving ? "Submitting..." : "Submit request"}
        </button>
        <button type="button" onClick={onCancel} className="btn btn-sm">Cancel</button>
      </div>
    </form>
  );
}

function IncidentRow({ assignment, canAct, onChange }) {
  const incident = assignment.incident;
  const [busy, setBusy] = useState(false);
  const [showRequestForm, setShowRequestForm] = useState(false);
  const [actionError, setActionError] = useState("");

  async function handleAcknowledge(e) {
    e.preventDefault();
    e.stopPropagation();
    setBusy(true);
    setActionError("");
    try {
      await acknowledgeAssignment(assignment.id);
      onChange();
    } catch (err) {
      setActionError(err?.response?.data?.detail || "Could not acknowledge");
    } finally {
      setBusy(false);
    }
  }

  async function handleStart(e) {
    e.preventDefault();
    e.stopPropagation();
    setBusy(true);
    setActionError("");
    try {
      await startAssignment(assignment.id);
      onChange();
    } catch (err) {
      setActionError(err?.response?.data?.detail || "Could not start work");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card card-sm">
      <Link
        to={`/incidents/${assignment.incident_id}`}
        style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 16, flexWrap: "wrap", textDecoration: "none", color: "inherit" }}
      >
        <div>
          <div style={{ fontWeight: 700 }}>{incident?.title || `Incident #${assignment.incident_id}`}</div>
          <div className="eyebrow" style={{ marginTop: 4 }}>
            {incident?.location} · {incident?.disaster_type}
            {assignment.is_lead ? <span style={{ color: "var(--accent)" }}> · Lead department</span> : null}
          </div>
          <div className="mono" style={{ color: "var(--text-muted)", fontSize: 12, marginTop: 4 }}>
            {assignment.status}
            {assignment.acknowledged_at ? ` · ack ${new Date(assignment.acknowledged_at).toLocaleString()}` : ""}
            {assignment.completed_at ? ` · done ${new Date(assignment.completed_at).toLocaleString()}` : ""}
          </div>
        </div>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          {incident?.severity ? <SeverityBadge severity={incident.severity} /> : null}
          <span className="link">Open →</span>
        </div>
      </Link>

      {canAct ? (
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 12, paddingTop: 12, borderTop: "1px solid var(--border)" }}>
          {assignment.status === "ASSIGNED" ? (
            <button onClick={handleAcknowledge} disabled={busy} className="btn btn-sm">Acknowledge</button>
          ) : null}
          {(assignment.status === "ASSIGNED" || assignment.status === "ACKNOWLEDGED") ? (
            <button onClick={handleStart} disabled={busy} className="btn btn-primary btn-sm">Start work</button>
          ) : null}
          {assignment.status === "IN_PROGRESS" ? (
            <Link to={`/incidents/${assignment.incident_id}`} className="btn btn-primary btn-sm" style={{ textDecoration: "none" }}>
              Submit action report
            </Link>
          ) : null}
          {assignment.status !== "COMPLETED" ? (
            <button
              onClick={(e) => { e.preventDefault(); e.stopPropagation(); setShowRequestForm((v) => !v); }}
              className="btn btn-sm"
            >
              {showRequestForm ? "Cancel request" : "Request more"}
            </button>
          ) : null}
        </div>
      ) : null}

      {actionError ? <div className="banner banner-danger" style={{ marginTop: 10, padding: 8, fontSize: 13 }}>{actionError}</div> : null}

      {showRequestForm ? (
        <RequestResourceForm
          assignment={assignment}
          onCancel={() => setShowRequestForm(false)}
          onDone={() => {
            setShowRequestForm(false);
            onChange();
          }}
        />
      ) : null}
    </div>
  );
}

export default function DepartmentDashboard() {
  const { user } = useAuth();
  const [departments, setDepartments] = useState([]);
  const [selectedDepartmentId, setSelectedDepartmentId] = useState(null);
  const [workload, setWorkload] = useState(null);
  const [activeTab, setActiveTab] = useState("pending");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDepartments()
      .then((data) => {
        setDepartments(data);
        const defaultId = user?.department_id || data[0]?.id || null;
        setSelectedDepartmentId(defaultId);
      })
      .catch((err) => setError(err?.response?.data?.detail || "Could not load departments"));
  }, [user]);

  function refresh() {
    if (!selectedDepartmentId) return;
    getDepartmentWorkload(selectedDepartmentId)
      .then((data) => {
        setWorkload(data);
        setError("");
      })
      .catch((err) => setError(err?.response?.data?.detail || "Could not load department workload"))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    setLoading(true);
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedDepartmentId]);

  const isDepartmentStaff = user?.role === "DEPARTMENT_STAFF";
  const rows = workload ? workload[activeTab] || [] : [];
  const selectedDept = departments.find((d) => d.id === selectedDepartmentId);
  // Staff act on their own department only; admins can act on any department they're viewing.
  const canAct = isDepartmentStaff ? user.department_id === selectedDepartmentId : user?.role === "ADMIN";

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">
            {isDepartmentStaff && selectedDept ? selectedDept.name : "Department dashboard"}
          </h1>
          <p className="page-subtitle">
            Acknowledge, start work, or request more resources right from the queue — no need to open
            each incident just to move it forward.
          </p>
        </div>
        {!isDepartmentStaff ? (
          <select
            value={selectedDepartmentId || ""}
            onChange={(e) => setSelectedDepartmentId(Number(e.target.value))}
            style={{ maxWidth: 260 }}
          >
            {departments.map((dept) => (
              <option key={dept.id} value={dept.id}>{dept.name}</option>
            ))}
          </select>
        ) : null}
      </div>

      {error ? <div className="banner banner-danger">{error}</div> : null}

      {workload ? (
        <div className="tabs">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={"tab" + (activeTab === tab.key ? " active" : "")}
            >
              {tab.label} <span className="mono">({workload.counts?.[tab.key] ?? 0})</span>
            </button>
          ))}
        </div>
      ) : null}

      <div style={{ display: "grid", gap: 12 }}>
        {loading ? (
          <div className="empty-state">Loading...</div>
        ) : rows.length === 0 ? (
          <div className="empty-state">Nothing in this queue right now.</div>
        ) : (
          rows.map((assignment) => (
            <IncidentRow key={assignment.id} assignment={assignment} canAct={canAct} onChange={refresh} />
          ))
        )}
      </div>
    </div>
  );
}
