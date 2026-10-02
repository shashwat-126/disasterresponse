import client from "./client";

async function downloadBlob(url, filename) {
  const response = await client.get(url, { responseType: "blob" });
  const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = blobUrl;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(blobUrl);
}

export async function downloadIncidentReport(incidentId) {
  await downloadBlob(`/incidents/${incidentId}/report`, `incident-${incidentId}-report.pdf`);
}

export async function downloadIncidentsCsv() {
  await downloadBlob("/incidents-export/csv", "incidents_export.csv");
}
