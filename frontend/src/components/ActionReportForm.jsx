import React from "react";
import { useState } from "react";
import { submitActionReport } from "../api/assignments";

export default function ActionReportForm({ assignmentId, onSubmitted, onCancel }) {
  const [officerName, setOfficerName] = useState("");
  const [teamMembers, setTeamMembers] = useState("");
  const [resourcesUsed, setResourcesUsed] = useState("");
  const [actionTaken, setActionTaken] = useState("");
  const [remarks, setRemarks] = useState("");
  const [arrivalTime, setArrivalTime] = useState("");
  const [completionTime, setCompletionTime] = useState("");
  const [proofFiles, setProofFiles] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const updated = await submitActionReport(assignmentId, {
        officerName,
        teamMembers,
        resourcesUsed,
        actionTaken,
        remarks,
        arrivalTime: arrivalTime ? new Date(arrivalTime).toISOString() : null,
        completionTime: completionTime ? new Date(completionTime).toISOString() : null,
        proofFiles,
      });
      onSubmitted?.(updated);
    } catch (err) {
      setError(err?.response?.data?.detail || "Could not submit action report");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card card-sm" style={{ display: "grid", gap: 14 }}>
      <div>
        <h3 style={{ fontSize: 16 }}>Submit action report</h3>
        <p className="page-subtitle" style={{ marginTop: 4 }}>
          This department can only be marked complete after this form is submitted.
        </p>
      </div>

      <div style={{ display: "grid", gap: 8 }}>
        <label className="eyebrow">Officer name *</label>
        <input value={officerName} onChange={(e) => setOfficerName(e.target.value)} required />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <div style={{ display: "grid", gap: 8 }}>
          <label className="eyebrow">Team members</label>
          <input
            value={teamMembers}
            onChange={(e) => setTeamMembers(e.target.value)}
            placeholder="Comma-separated names"
          />
        </div>
        <div style={{ display: "grid", gap: 8 }}>
          <label className="eyebrow">Resources used</label>
          <input value={resourcesUsed} onChange={(e) => setResourcesUsed(e.target.value)} />
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <div style={{ display: "grid", gap: 8 }}>
          <label className="eyebrow">Arrival time</label>
          <input type="datetime-local" value={arrivalTime} onChange={(e) => setArrivalTime(e.target.value)} />
        </div>
        <div style={{ display: "grid", gap: 8 }}>
          <label className="eyebrow">Completion time</label>
          <input
            type="datetime-local"
            value={completionTime}
            onChange={(e) => setCompletionTime(e.target.value)}
          />
        </div>
      </div>

      <div style={{ display: "grid", gap: 8 }}>
        <label className="eyebrow">Action taken *</label>
        <textarea rows={3} value={actionTaken} onChange={(e) => setActionTaken(e.target.value)} required />
      </div>

      <div style={{ display: "grid", gap: 8 }}>
        <label className="eyebrow">Remarks</label>
        <textarea rows={2} value={remarks} onChange={(e) => setRemarks(e.target.value)} />
      </div>

      <div style={{ display: "grid", gap: 8 }}>
        <label className="eyebrow">Proof (images, videos, or PDF reports)</label>
        <input
          type="file"
          multiple
          accept="image/*,video/*,.pdf"
          onChange={(e) => setProofFiles(Array.from(e.target.files || []))}
        />
      </div>

      {error ? <div className="banner banner-danger">{error}</div> : null}

      <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
        <button type="button" onClick={onCancel} className="btn">
          Cancel
        </button>
        <button type="submit" disabled={submitting} className="btn btn-primary">
          {submitting ? "Submitting..." : "Submit & mark complete"}
        </button>
      </div>
    </form>
  );
}
