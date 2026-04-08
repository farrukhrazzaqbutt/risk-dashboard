import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

function formatTime(ts) {
  const date = new Date(ts);
  return date.toLocaleTimeString();
}

export default function PnLChart({ data }) {
  return (
    <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 12 }}>
      <h3 style={{ margin: "0 0 12px", color: "#0f172a" }}>PnL Curve</h3>
      <div style={{ width: "100%", height: 300 }}>
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 8, right: 18, left: 0, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="ts" tickFormatter={formatTime} minTickGap={30} />
            <YAxis />
            <Tooltip
              labelFormatter={(value) => `Time: ${formatTime(value)}`}
              formatter={(value) => [Number(value).toFixed(2), "Total PnL"]}
            />
            <Line type="monotone" dataKey="total_pnl" stroke="#2563eb" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
