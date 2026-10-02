import React from "react";
import { assignmentStatusColors } from "../utils/constants";

export default function AssignmentStatusBadge({ status }) {
  const palette = assignmentStatusColors[status] || { bg: "#e5e7eb", text: "#374151" };
  return (
    <span className="badge" style={{ backgroundColor: palette.bg, color: palette.text }}>
      {status.replace("_", " ")}
    </span>
  );
}
