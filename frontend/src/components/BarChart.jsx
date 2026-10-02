import React from "react";

const DEFAULT_COLOR = "var(--accent)";

export default function BarChart({ data, colorMap = {} }) {
  const entries = Object.entries(data || {});
  const max = Math.max(1, ...entries.map(([, v]) => v));

  if (entries.length === 0) {
    return <div className="empty-state">No data yet.</div>;
  }

  return (
    <div style={{ display: "grid", gap: 10 }}>
      {entries.map(([label, value]) => (
        <div key={label} style={{ display: "grid", gridTemplateColumns: "110px 1fr 40px", alignItems: "center", gap: 10 }}>
          <div className="eyebrow" style={{ color: "var(--text-secondary)", textTransform: "none", letterSpacing: 0 }}>{label}</div>
          <div style={{ background: "var(--canvas)", borderRadius: 8, overflow: "hidden", height: 14 }}>
            <div
              style={{
                width: `${Math.max((value / max) * 100, 3)}%`,
                height: "100%",
                background: colorMap[label] || DEFAULT_COLOR,
                borderRadius: 8,
                transition: "width 0.3s ease",
              }}
            />
          </div>
          <div className="mono" style={{ fontSize: 13, fontWeight: 700, textAlign: "right" }}>{value}</div>
        </div>
      ))}
    </div>
  );
}
