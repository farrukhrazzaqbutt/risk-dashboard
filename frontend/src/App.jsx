import { useEffect, useMemo, useState } from "react";
import MetricCard from "./components/MetricCard";
import PnLChart from "./components/PnLChart";
import ClientPnLChart from "./components/ClientPnLChart";
import PriceStrip from "./components/PriceStrip";
import PositionsCard from "./components/PositionsCard";
import TradesTable from "./components/TradesTable";
import { log } from "./logger";

const pageStyle = {
  minHeight: "100vh",
  padding: "16px",
  background: "#f8fafc",
  color: "#0f172a",
  fontFamily: "Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
};

const gridStyle = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
  gap: "12px",
  marginBottom: "12px",
};

const layoutStyle = {
  display: "grid",
  gridTemplateColumns: "2fr 1fr",
  gap: "12px",
};

function numberFmt(value, digits = 2) {
  return Number(value || 0).toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  });
}

function getWsUrl() {
  const backend = import.meta.env.VITE_BACKEND_WS_URL;
  if (backend) {
    return backend;
  }
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const hostname = window.location.hostname || "localhost";
  return `${protocol}://${hostname}:8000/ws`;
}

export default function App() {
  const [snapshot, setSnapshot] = useState(null);
  const [status, setStatus] = useState("connecting");

  useEffect(() => {
    const url = getWsUrl();
    log.info("Opening WebSocket", { url });
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setStatus("connected");
      log.info("WebSocket connected", { url });
    };
    ws.onclose = (event) => {
      setStatus("disconnected");
      log.info("WebSocket closed", { code: event.code, reason: event.reason || undefined });
    };
    ws.onerror = () => {
      setStatus("error");
      log.warn("WebSocket error event (see network tab for details)", { url });
    };
    ws.onmessage = (event) => {
      try {
        setSnapshot(JSON.parse(event.data));
      } catch (err) {
        log.warn("Malformed WebSocket JSON frame", { error: String(err) });
      }
    };

    const ping = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send("ping");
      }
    }, 2000);

    return () => {
      clearInterval(ping);
      log.debug("Closing WebSocket");
      ws.close();
    };
  }, []);

  const metrics = useMemo(() => {
    if (!snapshot) {
      return {
        totalPnl: 0,
        realizedPnl: 0,
        unrealizedPnl: 0,
        monetization: 0,
        clientYield: 0,
        tradeCount: 0,
      };
    }
    return {
      totalPnl: snapshot.total_pnl,
      realizedPnl: snapshot.realized_pnl,
      unrealizedPnl: snapshot.unrealized_pnl,
      monetization: snapshot.monetization,
      clientYield: snapshot.client_yield,
      tradeCount: snapshot.trade_count,
    };
  }, [snapshot]);

  return (
    <div style={pageStyle}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <h1 style={{ margin: 0, fontSize: 24 }}>Risk Management Dashboard</h1>
        <span style={{ fontSize: 13, color: "#475569" }}>WebSocket: {status}</span>
      </div>

      <div style={gridStyle}>
        <MetricCard
          label="Total PnL"
          value={numberFmt(metrics.totalPnl)}
          tone={metrics.totalPnl >= 0 ? "positive" : "negative"}
        />
        <MetricCard
          label="Realized PnL"
          value={numberFmt(metrics.realizedPnl)}
          tone={metrics.realizedPnl >= 0 ? "positive" : "negative"}
        />
        <MetricCard
          label="Unrealized PnL"
          value={numberFmt(metrics.unrealizedPnl)}
          tone={metrics.unrealizedPnl >= 0 ? "positive" : "negative"}
        />
        <MetricCard label="Monetization" value={numberFmt(metrics.monetization)} tone="neutral" />
        <MetricCard label="Client Yield" value={numberFmt(metrics.clientYield)} tone="neutral" />
        <MetricCard label="Trade Count" value={numberFmt(metrics.tradeCount, 0)} tone="neutral" />
      </div>

      <div style={layoutStyle}>
        <div style={{ display: "grid", gap: "12px", minWidth: 0 }}>
          <PnLChart data={snapshot?.pnl_history || []} />
          <ClientPnLChart clientPnl={snapshot?.client_pnl} />
        </div>
        <div style={{ display: "grid", gap: "12px", alignContent: "start" }}>
          <PriceStrip prices={snapshot?.prices} />
          <PositionsCard positions={snapshot?.positions || []} />
        </div>
      </div>

      <div style={{ marginTop: 12, width: "100%", minWidth: 0 }}>
        <TradesTable trades={snapshot?.recent_trades || []} />
      </div>
    </div>
  );
}
