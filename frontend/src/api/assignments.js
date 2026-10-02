import client from "./client";

export async function getIncidentAssignments(incidentId) {
  const { data } = await client.get(`/incidents/${incidentId}/assignments`);
  return data;
}

export async function acknowledgeAssignment(assignmentId) {
  const { data } = await client.post(`/assignments/${assignmentId}/acknowledge`);
  return data;
}

export async function startAssignment(assignmentId) {
  const { data } = await client.post(`/assignments/${assignmentId}/start`);
  return data;
}

export async function submitActionReport(assignmentId, formValues) {
  const formData = new FormData();
  formData.append("officer_name", formValues.officerName);
  formData.append("action_taken", formValues.actionTaken);
  formData.append("team_members", formValues.teamMembers || "");
  formData.append("resources_used", formValues.resourcesUsed || "");
  formData.append("remarks", formValues.remarks || "");
  if (formValues.arrivalTime) formData.append("arrival_time", formValues.arrivalTime);
  if (formValues.completionTime) formData.append("completion_time", formValues.completionTime);
  (formValues.proofFiles || []).forEach((file) => formData.append("proof_files", file));

  const { data } = await client.post(`/assignments/${assignmentId}/action-report`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

// ---------------------------------------------------------------------------
// Admin coordination: pull in an extra department, reassign one, or drop one.
// ---------------------------------------------------------------------------

export async function addDepartmentToIncident(incidentId, departmentId) {
  const formData = new FormData();
  formData.append("department_id", departmentId);
  const { data } = await client.post(`/incidents/${incidentId}/assignments`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function reassignAssignment(assignmentId, departmentId) {
  const formData = new FormData();
  formData.append("department_id", departmentId);
  const { data } = await client.patch(`/assignments/${assignmentId}/reassign`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function removeAssignment(assignmentId) {
  const { data } = await client.delete(`/assignments/${assignmentId}`);
  return data;
}
