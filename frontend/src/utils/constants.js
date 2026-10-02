
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

// Values reference the CSS custom properties defined in styles/index.css so the
// semantic mapping (severity/status -> color) lives in exactly one place.
export const severityColors = {
  LOW: { bg: "var(--sev-low-bg)", text: "var(--sev-low-text)" },
  MEDIUM: { bg: "var(--sev-medium-bg)", text: "var(--sev-medium-text)" },
  HIGH: { bg: "var(--sev-high-bg)", text: "var(--sev-high-text)" },
  CRITICAL: { bg: "var(--sev-critical-bg)", text: "var(--sev-critical-text)" },
};

export const assignmentStatusColors = {
  ASSIGNED: { bg: "#eef1f6", text: "#475569" },
  ACKNOWLEDGED: { bg: "#e3edff", text: "#1d4ed8" },
  IN_PROGRESS: { bg: "var(--warning-soft)", text: "var(--warning)" },
  COMPLETED: { bg: "var(--live-soft)", text: "#15803d" },
};

export const resourceRequestColors = {
  PENDING: { bg: "var(--warning-soft)", text: "var(--warning)" },
  APPROVED: { bg: "#e3edff", text: "#1d4ed8" },
  FULFILLED: { bg: "var(--live-soft)", text: "#15803d" },
  REJECTED: { bg: "var(--danger-soft)", text: "var(--danger)" },
};

export const priorityColors = {
  P1: { bg: "var(--danger-soft)", text: "var(--danger)" },
  P2: { bg: "var(--warning-soft)", text: "#c2410c" },
  P3: { bg: "var(--sev-medium-bg)", text: "var(--sev-medium-text)" },
  P4: { bg: "var(--sev-low-bg)", text: "var(--sev-low-text)" },
};
