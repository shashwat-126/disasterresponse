import client from "./client";

export async function getActionReports({ departmentId, disasterType } = {}) {
  const params = {};
  if (departmentId) params.department_id = departmentId;
  if (disasterType) params.disaster_type = disasterType;
  const { data } = await client.get("/action-reports", { params });
  return data;
}
