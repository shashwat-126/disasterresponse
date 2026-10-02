import client from "./client";

export async function uploadAttachments(incidentId, files) {
  if (!files || files.length === 0) return [];
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  const { data } = await client.post(`/incidents/${incidentId}/attachments`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function getAttachments(incidentId) {
  const { data } = await client.get(`/incidents/${incidentId}/attachments`);
  return data;
}
