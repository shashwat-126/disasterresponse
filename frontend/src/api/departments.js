import client from "./client";

export async function getDepartments() {
  const { data } = await client.get("/departments");
  return data;
}

export async function getDepartmentIncidents(departmentId) {
  const { data } = await client.get(`/departments/${departmentId}/incidents`);
  return data;
}

export async function getDepartmentWorkload(departmentId) {
  const { data } = await client.get(`/departments/${departmentId}/workload`);
  return data;
}
