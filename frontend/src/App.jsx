import { useMemo, useState } from "react";
import api from "./services/api";
import {
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import "./App.css";



const fieldConfig = [
  {
    name: "stop_loss_points",
    label: "Stop Loss Points",
    tooltip: "Exit the trade if price moves against you by this many points.",
  },
  {
    name: "take_profit_points",
    label: "Take Profit Points",
    tooltip: "Exit the trade once the target profit is reached.",
  },
  {
    name: "quantity",
    label: "Quantity",
    tooltip: "Number of units/contracts per trade.",
  },
  {
    name: "max_trades_per_day",
    label: "Max Trades Per Day",
    tooltip: "Maximum trades allowed in a single trading day.",
  },
  {
    name: "cost_per_trade",
    label: "Cost Per Trade",
    tooltip: "Brokerage, slippage, or transaction cost per trade.",
  },
  {
    name: "bollinger_period",
    label: "Bollinger Period",
    tooltip: "Number of candles used to calculate Bollinger Bands.",
  },
  {
    name: "bollinger_multiplier",
    label: "Bollinger Multiplier",
    tooltip: "Standard deviation multiplier for Bollinger Bands.",
  },
  {
    name: "rows_limit",
    label: "Rows Limit",
    tooltip: "Maximum number of data rows to process in the backtest.",
  },
];

function formatMetricLabel(key) {
  return key
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatMetricValue(key, value) {
  if (value === null || value === undefined || value === "") return "-";

  const numericValue = Number(value);
  const isNumber = !Number.isNaN(numericValue);

  if (key === "win_rate" && isNumber) {
    return `${numericValue}%`;
  }

  if (
    ["profit_factor", "avg_trade_pnl", "avg_win", "avg_loss", "total_net_pnl", "max_drawdown"].includes(key) &&
    isNumber
  ) {
    return Number.isInteger(numericValue)
      ? numericValue.toLocaleString()
      : numericValue.toFixed(2);
  }

  return String(value);
}

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
      setResult(response.data);
    } catch (err) {
      console.error("Backtest failed:", err);
      setError(
        "Backtest failed. Please try again in a few seconds or check backend logs."
      );
    } finally {
      setLoading(false);
    }
  };

  const metrics = result?.metrics ?? {};
  const dailySummary = Array.isArray(result?.daily_summary)
    ? result.daily_summary
    : [];
  const tradeLog = Array.isArray(result?.trade_log) ? result.trade_log : [];

  const chartData = useMemo(() => {
    return dailySummary.map((row, index) => ({
      id: index + 1,
      trade_date: String(row.trade_date ?? ""),
      cumulative_pnl: Number(row.cumulative_pnl ?? 0),
    }));
  }, [dailySummary]);

  return (
    <div className="page">
      <div className="page__glow page__glow--one" />
      <div className="page__glow page__glow--two" />

      <main className="container">
        <section className="hero">
          <span className="hero__badge">Live Strategy Dashboard</span>
          <h1 className="hero__title">Mini Quant Backtester</h1>
          <p className="hero__subtitle">
            Run a quick intraday backtest, tune the strategy inputs, and review
            key performance metrics, equity curve, and trade-level results.
          </p>
        </section>

        <section className="panel form-panel">
          <div className="panel__header">
            <div>
              <h2 className="panel__title">Strategy Inputs</h2>
              <p className="panel__subtitle">
                Update the parameters below and run the backtest.
              </p>
            </div>
          </div>

          <div className="form-grid">
            {fieldConfig.map((field) => (
              <div className="form-field" key={field.name}>
              <div className="form-field__label-row">
                <label className="form-field__label" htmlFor={field.name}>
                  {field.label}
                </label>

                <div className="tooltip">
                  ?
                  <span className="tooltip-text">{field.tooltip}</span>
                </div>
              </div>

              <input
                id={field.name}
                className="form-field__input"
                name={field.name}
                type="number"
                value={formData[field.name]}
                onChange={handleChange}
              />
            </div>
            ))}
          </div>

          <div className="form-actions">
            <button
              className="primary-btn"
              onClick={runBacktest}
              disabled={loading}
            >
              {loading ? "Running Backtest..." : "Run Backtest"}
            </button>
          </div>

          {error && <div className="alert alert--error">{error}</div>}
        </section>

        {result && (
          <>
            <section className="panel">
              <div className="panel__header">
                <div>
                  <h2 className="panel__title">Performance Metrics</h2>
                  <p className="panel__subtitle">
                    Quick summary of the strategy’s backtest performance.
                  </p>
                </div>
              </div>

              <div className="metrics-grid">
                {Object.entries(metrics).map(([key, value]) => (
                  <div className="metric-card" key={key}>
                    <div className="metric-card__label">
                      {formatMetricLabel(key)}
                    </div>
                    <div className="metric-card__value">{formatMetricValue(key, value)}</div>
                  </div>
                ))}
              </div>
            </section>

            <section className="panel">
              <div className="panel__header">
                <div>
                  <h2 className="panel__title">Equity Curve</h2>
                  <p className="panel__subtitle">
                    Cumulative P&amp;L trend across the backtest period.
                  </p>
                </div>
              </div>

              <div className="chart-card chart-card--dark">
                <ResponsiveContainer width="100%" height={380}>
                  <AreaChart
                    data={chartData}
                    margin={{ top: 10, right: 20, left: 0, bottom: 10 }}
                  >
                    <defs>
                      <linearGradient id="equityFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#22c55e" stopOpacity={0.35} />
                        <stop offset="100%" stopColor="#22c55e" stopOpacity={0.03} />
                      </linearGradient>
                    </defs>

                    <CartesianGrid
                      stroke="rgba(148, 163, 184, 0.12)"
                      vertical={false}
                    />

                    <XAxis
                      dataKey="trade_date"
                      tick={{ fill: "#94a3b8", fontSize: 12 }}
                      tickLine={false}
                      axisLine={false}
                      minTickGap={30}
                    />

                    <YAxis
                      tick={{ fill: "#94a3b8", fontSize: 12 }}
                      tickLine={false}
                      axisLine={false}
                      tickFormatter={(value) => `${value}`}
                    />

                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#0f172a",
                        border: "1px solid rgba(148, 163, 184, 0.2)",
                        borderRadius: "12px",
                        color: "#e2e8f0",
                      }}
                      labelStyle={{ color: "#cbd5e1", marginBottom: "6px" }}
                      formatter={(value) => [`${value}`, "Cumulative P&L"]}
                    />

                    <ReferenceLine
                      y={0}
                      stroke="rgba(255,255,255,0.22)"
                      strokeDasharray="4 4"
                    />

                    <Area
                      type="monotone"
                      dataKey="cumulative_pnl"
                      stroke="#22c55e"
                      strokeWidth={3}
                      fill="url(#equityFill)"
                    />

                    <Line
                      type="monotone"
                      dataKey="cumulative_pnl"
                      stroke="#22c55e"
                      strokeWidth={3}
                      dot={false}
                      activeDot={{ r: 5 }}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </section>

            <section className="panel">
              <div className="panel__header">
                <div>
                  <h2 className="panel__title">Daily Summary</h2>
                  <p className="panel__subtitle">
                    Day-level rollup of trades and profitability.
                  </p>
                </div>
              </div>

              <div className="table-wrap">
                <table className="data-table">
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
            </section>

            <section className="panel">
              <div className="panel__header">
                <div>
                  <h2 className="panel__title">Trade Log</h2>
                  <p className="panel__subtitle">
                    Trade-level execution details for review.
                  </p>
                </div>
              </div>

              <div className="table-wrap">
                <table className="data-table">
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
            </section>

            <details className="debug-box">
              <summary>Debug Response</summary>
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </details>
          </>
        )}
      </main>
    </div>
  );
}

export default App;