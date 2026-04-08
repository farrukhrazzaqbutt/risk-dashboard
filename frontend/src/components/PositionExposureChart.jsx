import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from "recharts";

function toRows(positions) {
  if (!Array.isArray(positions)) return [];
  return [...positions]
    .map((p) => ({
      symbol: p.symbol,
      qty: Number(p.quantity),
    }))
    .sort((a, b) => Math.abs(b.qty) - Math.abs(a.qty));
}

export default function PositionExposureChart({ positions }) {
  const data = toRows(positions);
  if (data.length === 0) {
    return null;
  }

  const maxAbs = Math.max(...data.map((d) => Math.abs(d.qty)), 1);

  return (
    <div style={{ marginTop: 16, paddingTop: 14, borderTop: "1px solid #e2e8f0" }}>
      <h4 style={{ margin: "0 0 6px", color: "#0f172a", fontSize: 14 }}>Net exposure (quantity)</h4>
      <p style={{ margin: "0 0 10px", fontSize: 12, color: "#64748b", lineHeight: 1.4 }}>
        Signed position size: long (green) vs short (red). Mirrors the desk rule — client buys → we are short.
      </p>
      <div style={{ width: "100%", height: 220 }}>
        <ResponsiveContainer>
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 2, right: 10, left: 4, bottom: 2 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              type="number"
              domain={[-maxAbs * 1.1, maxAbs * 1.1]}
              tickFormatter={(v) => Number(v).toLocaleString(undefined, { maximumFractionDigits: 0 })}
            />
            <YAxis type="category" dataKey="symbol" width={68} tick={{ fontSize: 11 }} />
            <Tooltip
              formatter={(value) => [Number(value).toLocaleString(undefined, { maximumFractionDigits: 0 }), "Qty"]}
              labelFormatter={(label) => label}
            />
            <ReferenceLine x={0} stroke="#64748b" strokeWidth={1} />
            <Bar dataKey="qty" radius={[0, 4, 4, 0]} maxBarSize={22}>
              {data.map((entry) => (
                <Cell key={entry.symbol} fill={entry.qty >= 0 ? "#166534" : "#991b1b"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
