function fmtPrice(symbol, v) {
  const abs = Math.abs(v);
  const digits = symbol === "XAUUSD" ? 2 : symbol === "USDJPY" ? 3 : 5;
  return Number(v).toLocaleString(undefined, { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

export default function PriceStrip({ prices }) {
  const rows = prices && typeof prices === "object" ? Object.values(prices) : [];
  if (rows.length === 0) {
    return (
      <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 12 }}>
        <h3 style={{ margin: "0 0 8px", color: "#0f172a", fontSize: 15 }}>Live quotes</h3>
        <p style={{ margin: 0, fontSize: 13, color: "#94a3b8" }}>Waiting for prices…</p>
      </div>
    );
  }

  return (
    <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 12 }}>
      <h3 style={{ margin: "0 0 10px", color: "#0f172a", fontSize: 15 }}>Live bid / ask / mid</h3>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {rows.map((p) => (
          <div
            key={p.symbol}
            style={{
              display: "grid",
              gridTemplateColumns: "88px 1fr 1fr 1fr",
              gap: 8,
              alignItems: "center",
              fontSize: 13,
              borderBottom: "1px solid #f1f5f9",
              paddingBottom: 6,
            }}
          >
            <span style={{ fontWeight: 700, color: "#0f172a" }}>{p.symbol}</span>
            <span style={{ color: "#b45309" }} title="Bid">
              B {fmtPrice(p.symbol, p.bid)}
            </span>
            <span style={{ color: "#0f766e" }} title="Ask">
              A {fmtPrice(p.symbol, p.ask)}
            </span>
            <span style={{ color: "#475569" }} title="Mid">
              M {fmtPrice(p.symbol, p.mid)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
