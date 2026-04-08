import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from "recharts";

function dictToRows(dict) {
  if (!dict || typeof dict !== "object") return [];
  return Object.entries(dict)
    .map(([client_id, value]) => ({ client_id, value: Number(value) }))
    .sort((a, b) => a.client_id.localeCompare(b.client_id));
}

export default function ClientPnLChart({ clientPnl }) {
  const data = dictToRows(clientPnl);

  return (
    <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 12 }}>
      <h3 style={{ margin: "0 0 8px", color: "#0f172a", fontSize: 15 }}>Client PnL (cumulative proxy)</h3>
      <p style={{ margin: "0 0 12px", fontSize: 12, color: "#64748b" }}>Simplified client-side view vs our book</p>
      <div style={{ width: "100%", height: 300 }}>
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 4, right: 12, left: 4, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="client_id" tick={{ fontSize: 11 }} />
            <YAxis tickFormatter={(v) => Number(v).toFixed(0)} />
            <Tooltip formatter={(v) => [Number(v).toFixed(2), "Client PnL"]} />
            <ReferenceLine y={0} stroke="#94a3b8" />
            <Bar dataKey="value" name="PnL" radius={[4, 4, 0, 0]}>
              {data.map((entry) => (
                <Cell key={entry.client_id} fill={entry.value >= 0 ? "#0f766e" : "#c2410c"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
