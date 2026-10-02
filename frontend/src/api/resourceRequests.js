import client from "./client";

export async function getIncidentResourceRequests(incidentId) {
  const { data } = await client.get(`/incidents/${incidentId}/resource-requests`);
  return data;
}

export async function createResourceRequest(incidentId, { resourceType, quantity, justification, departmentId }) {
  const { data } = await client.post(`/incidents/${incidentId}/resource-requests`, {
    resource_type: resourceType,
    quantity: Number(quantity),
    justification,
    department_id: departmentId || null,
  });
  return data;
}

export async function resolveResourceRequest(requestId, status, resolutionNotes = "") {
  const { data } = await client.patch(`/resource-requests/${requestId}`, {
    status,
    resolution_notes: resolutionNotes,
  });
  return data;
}

export async function getAllResourceRequests(statusFilter) {
  const { data } = await client.get("/resource-requests", {
    params: statusFilter ? { status_filter: statusFilter } : {},
  });
  return data;
}
