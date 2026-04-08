import PositionExposureChart from "./PositionExposureChart";

function numberFmt(value, digits = 2) {
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits });
}

export default function PositionsCard({ positions }) {
  return (
    <div style={{ background: "#fff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 12 }}>
      <h3 style={{ margin: "0 0 12px", color: "#0f172a" }}>Positions by Instrument</h3>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
          <thead>
            <tr style={{ textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>
              <th style={{ padding: "8px 6px" }}>Instrument</th>
              <th style={{ padding: "8px 6px" }}>Quantity</th>
              <th style={{ padding: "8px 6px" }}>Avg Price</th>
              <th style={{ padding: "8px 6px" }}>Market</th>
              <th style={{ padding: "8px 6px" }}>Unrealized PnL</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((pos) => (
              <tr key={pos.symbol} style={{ borderBottom: "1px solid #f1f5f9" }}>
                <td style={{ padding: "8px 6px", fontWeight: 600 }}>{pos.symbol}</td>
                <td style={{ padding: "8px 6px" }}>{numberFmt(pos.quantity, 0)}</td>
                <td style={{ padding: "8px 6px" }}>{numberFmt(pos.avg_price, 5)}</td>
                <td style={{ padding: "8px 6px" }}>{numberFmt(pos.market_price, 5)}</td>
                <td style={{ padding: "8px 6px", color: pos.unrealized_pnl >= 0 ? "#166534" : "#991b1b" }}>
                  {numberFmt(pos.unrealized_pnl)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <PositionExposureChart positions={positions} />
    </div>
  );
}
