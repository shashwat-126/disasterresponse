import React from "react";

export default function TrendChart({ series }) {
  if (!series || series.length === 0) {
    return <div className="empty-state">No trend data yet.</div>;
  }

  const width = 640;
  const height = 140;
  const padding = 20;
  const max = Math.max(1, ...series.map((p) => p.count));
  const stepX = (width - padding * 2) / Math.max(series.length - 1, 1);

  const points = series.map((p, i) => {
    const x = padding + i * stepX;
    const y = height - padding - (p.count / max) * (height - padding * 2);
    return `${x},${y}`;
  });

  return (
    <svg viewBox={`0 0 ${width} ${height}`} style={{ width: "100%", height: "auto" }}>
      <polyline points={points.join(" ")} fill="none" stroke="var(--accent)" strokeWidth="2.5" />
      {series.map((p, i) => {
        const [x, y] = points[i].split(",");
        return <circle key={p.date} cx={x} cy={y} r="2.5" fill="var(--accent)" />;
      })}
      <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="var(--border)" strokeWidth="1" />
    </svg>
  );
}
