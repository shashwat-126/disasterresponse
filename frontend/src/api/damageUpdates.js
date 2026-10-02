import client from "./client";

export async function getIncidentDamageUpdates(incidentId) {
  const { data } = await client.get(`/incidents/${incidentId}/damage-updates`);
  return data;
}

export async function createDamageUpdate(
  incidentId,
  { description, revisedPeopleAffected, revisedInjuries, severityReassessment, departmentId }
) {
  const { data } = await client.post(`/incidents/${incidentId}/damage-updates`, {
    description,
    revised_people_affected: revisedPeopleAffected === "" ? null : Number(revisedPeopleAffected),
    revised_injuries: revisedInjuries === "" ? null : Number(revisedInjuries),
    severity_reassessment: severityReassessment || null,
    department_id: departmentId || null,
  });
  return data;
}
