import React from "react";
import { useNavigate } from "react-router-dom";
import IncidentForm from "../components/IncidentForm";
import { uploadAttachments } from "../api/attachments";
import { createIncident } from "../api/incidents";

export default function SubmitIncident() {
  const navigate = useNavigate();

  async function handleSubmit(payload, files) {
    const incident = await createIncident(payload);
    if (files && files.length > 0) {
      try {
        await uploadAttachments(incident.id, files);
      } catch (err) {
        console.error("Attachment upload failed:", err);
      }
    }
    navigate(`/incidents/${incident.id}`);
  }

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Submit incident</h1>
          <p className="page-subtitle">
            Capture the minimum operational details required for AI severity prediction and resource
            allocation. The system auto-assigns responding departments once this is submitted.
          </p>
        </div>
      </div>
      <div className="card" style={{ maxWidth: 720 }}>
        <IncidentForm onSubmit={handleSubmit} />
      </div>
    </div>
  );
}
