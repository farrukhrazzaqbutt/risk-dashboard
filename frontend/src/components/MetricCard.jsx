const cardStyle = {
  background: "#ffffff",
  border: "1px solid #e2e8f0",
  borderRadius: "8px",
  padding: "14px",
  minHeight: "88px",
};

const labelStyle = {
  fontSize: "12px",
  color: "#475569",
  marginBottom: "8px",
  textTransform: "uppercase",
  letterSpacing: "0.04em",
};

const valueStyle = {
  fontSize: "24px",
  fontWeight: 700,
  color: "#0f172a",
};

export default function MetricCard({ label, value, tone }) {
  const color = tone === "positive" ? "#166534" : tone === "negative" ? "#991b1b" : "#0f172a";

  return (
    <div style={cardStyle}>
      <div style={labelStyle}>{label}</div>
      <div style={{ ...valueStyle, color }}>{value}</div>
    </div>
  );
}
