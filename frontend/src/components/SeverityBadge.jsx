import React from "react";
import { severityColors } from "../utils/constants";

export default function SeverityBadge({ severity }) {
  const palette = severityColors[severity] || { bg: "#e5e7eb", text: "#374151" };
  return (
    <span className="badge" style={{ backgroundColor: palette.bg, color: palette.text }}>
      {severity}
    </span>
  );
}
