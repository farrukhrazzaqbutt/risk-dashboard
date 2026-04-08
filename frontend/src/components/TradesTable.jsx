function numberFmt(value, digits = 2) {
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits });
}

function formatTime(ts) {
  return new Date(ts).toLocaleTimeString();
}

export default function TradesTable({ trades }) {
  return (
    <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 12 }}>
      <h3 style={{ margin: "0 0 12px", color: "#0f172a" }}>Recent Trades</h3>
      <div
        style={{
          maxHeight: 280,
          overflowY: "auto",
          overflowX: "auto",
          border: "1px solid #f1f5f9",
          borderRadius: 6,
        }}
      >
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>
              {["ID", "Client", "Instrument", "Side", "Quantity", "Price", "Time"].map((label) => (
                <th
                  key={label}
                  style={{
                    padding: "8px 6px",
                    position: "sticky",
                    top: 0,
                    background: "#fff",
                    zIndex: 1,
                    boxShadow: "0 1px 0 #e2e8f0",
                  }}
                >
                  {label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {trades.map((t) => (
              <tr key={t.trade_id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                <td style={{ padding: "8px 6px" }}>{t.trade_id}</td>
                <td style={{ padding: "8px 6px" }}>{t.client_id}</td>
                <td style={{ padding: "8px 6px", fontWeight: 600 }}>{t.symbol}</td>
                <td style={{ padding: "8px 6px", color: t.side === "BUY" ? "#0f766e" : "#b45309" }}>{t.side}</td>
                <td style={{ padding: "8px 6px" }}>{numberFmt(t.quantity, 0)}</td>
                <td style={{ padding: "8px 6px" }}>{numberFmt(t.price, 5)}</td>
                <td style={{ padding: "8px 6px" }}>{formatTime(t.ts)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
