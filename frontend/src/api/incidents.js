import client from "./client";
export async function createIncident(payload) { const { data } = await client.post("/incidents", payload); return data; }
export async function getIncidents() { const { data } = await client.get("/incidents"); return data; }
export async function getIncident(id) { const { data } = await client.get(`/incidents/${id}`); return data; }
export async function updateIncidentStatus(id, status) { const { data } = await client.patch(`/incidents/${id}/status`, { status }); return data; }
export async function getAllocation(id) { const { data } = await client.get(`/incidents/${id}/allocation`); return data; }
