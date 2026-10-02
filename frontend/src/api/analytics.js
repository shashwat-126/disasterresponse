import client from "./client";

export async function getDistribution() {
  const { data } = await client.get("/analytics/distribution");
  return data;
}

export async function getDepartmentPerformance() {
  const { data } = await client.get("/analytics/department-performance");
  return data;
}

export async function getSlaOverview() {
  const { data } = await client.get("/analytics/sla");
  return data;
}

export async function getTrend(days = 30) {
  const { data } = await client.get("/analytics/trend", { params: { days } });
  return data;
}

export async function getAuditLogs(params = {}) {
  const { data } = await client.get("/audit-logs", { params });
  return data;
}
