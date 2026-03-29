import { useMemo, useState } from "react";
import api from "./services/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

function App() {
  const [formData, setFormData] = useState({
  stop_loss_points: 30,
  take_profit_points: 60,
  quantity: 20,
  max_trades_per_day: 2,
  cost_per_trade: 20,
  bollinger_period: 20,
  bollinger_multiplier: 2,
  rows_limit: 5000,
});

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
  const { name, value } = e.target;
  setFormData((prev) => ({
    ...prev,
    [name]: Number(value),
  }));
};

  const runBacktest = async () => {
    try {
      setLoading(true);
      setError("");
      setResult(null);

      const response = await api.post("/run-backtest", formData);
      console.log("Backtest response:", response.data);
      setResult(response.data);
    } catch (err) {
      console.error("Backtest failed:", err);
      setError("Backtest failed. Check browser console and backend logs.");
    } finally {
      setLoading(false);
    }
  };

  const metrics = result?.metrics ?? {};
  const dailySummary = Array.isArray(result?.daily_summary) ? result.daily_summary : [];
  const tradeLog = Array.isArray(result?.trade_log) ? result.trade_log : [];

  const chartData = useMemo(() => {
    return dailySummary.map((row, index) => ({
      id: index + 1,
      trade_date: String(row.trade_date ?? ""),
      cumulative_pnl: Number(row.cumulative_pnl ?? 0),
    }));
  }, [dailySummary]);

  return (
    <div style={{ padding: "24px", fontFamily: "Arial, sans-serif", color: "white" }}>
      <h1 style={{ marginBottom: "24px" }}>Mini Quant Backtester</h1>

      <div
        style={{
          display: "grid",
          gap: "12px",
          maxWidth: "520px",
          marginBottom: "24px",
        }}
      >
        
        <input name="stop_loss_points" value={formData.stop_loss_points} onChange={handleChange} placeholder="Stop Loss" />
        <input name="take_profit_points" value={formData.take_profit_points} onChange={handleChange} placeholder="Take Profit" />
        <input name="quantity" value={formData.quantity} onChange={handleChange} placeholder="Quantity" />
        <input name="max_trades_per_day" value={formData.max_trades_per_day} onChange={handleChange} placeholder="Max Trades Per Day" />
        <input name="cost_per_trade" value={formData.cost_per_trade} onChange={handleChange} placeholder="Cost Per Trade" />
        <input name="bollinger_period" value={formData.bollinger_period} onChange={handleChange} placeholder="Bollinger Period" />
        <input name="bollinger_multiplier" value={formData.bollinger_multiplier} onChange={handleChange} placeholder="Bollinger Multiplier" />
        <input name="rows_limit" value={formData.rows_limit} onChange={handleChange} placeholder="Rows Limit" />

        <button onClick={runBacktest} disabled={loading}>
          {loading ? "Running..." : "Run Backtest"}
        </button>
      </div>

      {error && <p style={{ color: "#ff6b6b" }}>{error}</p>}

      {result && (
        <div>
          <h2>Metrics</h2>
          <div
            style={{
              display: "flex",
              gap: "16px",
              flexWrap: "wrap",
              marginBottom: "32px",
            }}
          >
            {Object.entries(metrics).map(([key, value]) => (
              <div
                key={key}
                style={{
                  padding: "12px",
                  border: "1px solid #444",
                  borderRadius: "8px",
                  minWidth: "160px",
                  background: "#111827",
                }}
              >
                <div style={{ fontSize: "12px", opacity: 0.8 }}>{key}</div>
                <div style={{ fontSize: "20px", fontWeight: "bold", marginTop: "6px" }}>
                  {String(value)}
                </div>
              </div>
            ))}
          </div>

          <h2>Equity Curve</h2>
          <div style={{ width: "100%", height: 320, background: "white", padding: "8px", borderRadius: "8px", marginBottom: "32px" }}>
            <ResponsiveContainer>
              <LineChart data={chartData}>
                <CartesianGrid stroke="#ccc" />
                <XAxis dataKey="trade_date" hide={chartData.length > 25} />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="cumulative_pnl"
                  stroke="#00aa66"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <h2>Daily Summary</h2>
          <div style={{ overflowX: "auto", marginBottom: "32px" }}>
            <table border="1" cellPadding="8" style={{ borderCollapse: "collapse", width: "100%", background: "white", color: "black" }}>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Trades</th>
                  <th>Gross PnL</th>
                  <th>Cost</th>
                  <th>Net PnL</th>
                  <th>Cumulative PnL</th>
                </tr>
              </thead>
              <tbody>
                {dailySummary.slice(0, 100).map((row, i) => (
                  <tr key={i}>
                    <td>{String(row.trade_date ?? "")}</td>
                    <td>{String(row.trades_count ?? "")}</td>
                    <td>{String(row.gross_pnl ?? "")}</td>
                    <td>{String(row.cost ?? "")}</td>
                    <td>{String(row.net_pnl ?? "")}</td>
                    <td>{String(row.cumulative_pnl ?? "")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h2>Trade Log</h2>
          <div style={{ overflowX: "auto" }}>
            <table border="1" cellPadding="6" style={{ borderCollapse: "collapse", width: "100%", background: "white", color: "black" }}>
              <thead>
                <tr>
                  <th>Trade Date</th>
                  <th>Entry Time</th>
                  <th>Exit Time</th>
                  <th>Entry Price</th>
                  <th>Exit Price</th>
                  <th>Quantity</th>
                  <th>Exit Reason</th>
                  <th>Net PnL</th>
                </tr>
              </thead>
              <tbody>
                {tradeLog.slice(0, 50).map((row, i) => (
                  <tr key={i}>
                    <td>{String(row.trade_date ?? "")}</td>
                    <td>{String(row.entry_time ?? "")}</td>
                    <td>{String(row.exit_time ?? "")}</td>
                    <td>{String(row.entry_price ?? "")}</td>
                    <td>{String(row.exit_price ?? "")}</td>
                    <td>{String(row.quantity ?? "")}</td>
                    <td>{String(row.exit_reason ?? "")}</td>
                    <td>{String(row.net_pnl ?? "")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <details style={{ marginTop: "24px" }}>
            <summary>Debug response</summary>
            <pre style={{ whiteSpace: "pre-wrap", color: "white" }}>
              {JSON.stringify(result, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}

export default App;