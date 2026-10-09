import { useState } from "react";

import {
  Search,
  TrendingUp,
  TrendingDown,
  Activity,
  BarChart3,
} from "lucide-react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import api from "../api/api";

import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";


function StockExplorer() {
  const [ticker, setTicker] = useState("AAPL");

  const [stockInfo, setStockInfo] = useState(null);

  const [history, setHistory] = useState([]);

  const [indicators, setIndicators] = useState([]);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");


  const loadStock = async () => {
    try {
      setLoading(true);
      setError("");

      const symbol = ticker
        .trim()
        .toUpperCase();

      if (!symbol) {
        setError(
          "Please enter a stock ticker."
        );

        return;
      }


      const [
        stockResponse,
        historyResponse,
        indicatorsResponse,
      ] = await Promise.all([
        api.get(
          `/stocks/${symbol}`
        ),

        api.get(
          `/stocks/${symbol}/history?limit=150`
        ),

        api.get(
          `/stocks/${symbol}/indicators?limit=150`
        ),
      ]);


      setStockInfo(
        stockResponse.data
      );


      const historyData =
        extractArray(
          historyResponse.data
        );


      const indicatorData =
        extractArray(
          indicatorsResponse.data
        );


      const sortedHistory =
        [...historyData].sort(
          (a, b) =>
            new Date(a.date) -
            new Date(b.date)
        );


      const sortedIndicators =
        [...indicatorData].sort(
          (a, b) =>
            new Date(a.date) -
            new Date(b.date)
        );


      setHistory(
        sortedHistory
      );

      setIndicators(
        sortedIndicators
      );

    } catch (err) {
      console.error(
        "Stock loading error:",
        err
      );

      setError(
        err?.response?.data?.detail ||
        "Unable to load stock information."
      );

    } finally {
      setLoading(false);
    }
  };


  const latestHistory =
    history.length > 0
      ? history[
          history.length - 1
        ]
      : null;


  const previousHistory =
    history.length > 1
      ? history[
          history.length - 2
        ]
      : null;


  const latestIndicator =
    indicators.length > 0
      ? indicators[
          indicators.length - 1
        ]
      : null;


  const currentPrice =
    getNumber(
      stockInfo?.close ??
      stockInfo?.latest_close ??
      stockInfo?.current_price ??
      latestHistory?.close
    );


  const previousPrice =
    getNumber(
      previousHistory?.close
    );


  const dailyChange =
    currentPrice !== null &&
    previousPrice !== null
      ? currentPrice -
        previousPrice
      : null;


  const dailyChangePercent =
    currentPrice !== null &&
    previousPrice !== null &&
    previousPrice !== 0
      ? (
          dailyChange /
          previousPrice
        ) * 100
      : null;


  const isPositive =
    dailyChange !== null
      ? dailyChange >= 0
      : true;


  const chartData =
    mergeChartData(
      history,
      indicators
    );


  return (
    <div>

      {/* =============================
          HEADER
      ============================== */}

      <div className="page-header">

        <div>

          <h1>
            Stock Explorer
          </h1>

          <p>
            Explore historical prices,
            OHLCV data and technical
            indicators.
          </p>

        </div>

      </div>


      {/* =============================
          SEARCH
      ============================== */}

      <div className="card stock-search-panel">

        <div className="stock-search-input">

          <Search size={19} />

          <input
            value={ticker}
            onChange={
              (event) =>
                setTicker(
                  event.target.value
                )
            }
            onKeyDown={
              (event) => {
                if (
                  event.key === "Enter"
                ) {
                  loadStock();
                }
              }
            }
            placeholder="Enter ticker e.g. AAPL"
          />

        </div>


        <button
          type="button"
          className="primary-button"
          onClick={loadStock}
        >
          Search Stock
        </button>

      </div>


      {/* =============================
          LOADING
      ============================== */}

      {loading && (
        <Loading
          text="Loading stock data..."
        />
      )}


      {/* =============================
          ERROR
      ============================== */}

      {error && (
        <ErrorMessage
          message={error}
        />
      )}


      {/* =============================
          STOCK SUMMARY
      ============================== */}

      {!loading &&
        latestHistory && (

        <>

          <div className="stock-title-row">

            <div>

              <span className="stock-symbol">
                {ticker
                  .trim()
                  .toUpperCase()}
              </span>

              <span className="stock-date">
                Latest dataset date:
                {" "}
                {latestHistory.date}
              </span>

            </div>


            <div className="stock-main-price">

              <strong>
                {formatCurrency(
                  currentPrice
                )}
              </strong>


              {dailyChangePercent !== null && (

                <span
                  className={
                    isPositive
                      ? "stock-change positive-text"
                      : "stock-change negative-text"
                  }
                >

                  {isPositive
                    ? <TrendingUp size={17} />
                    : <TrendingDown size={17} />
                  }

                  {isPositive
                    ? "+"
                    : ""
                  }

                  {dailyChangePercent.toFixed(
                    2
                  )}
                  %

                </span>

              )}

            </div>

          </div>


          {/* =============================
              OHLCV CARDS
          ============================== */}

          <div className="stock-metrics-grid">

            <MetricCard
              title="Open"
              value={
                formatCurrency(
                  latestHistory.open
                )
              }
            />

            <MetricCard
              title="High"
              value={
                formatCurrency(
                  latestHistory.high
                )
              }
            />

            <MetricCard
              title="Low"
              value={
                formatCurrency(
                  latestHistory.low
                )
              }
            />

            <MetricCard
              title="Close"
              value={
                formatCurrency(
                  latestHistory.close
                )
              }
            />

            <MetricCard
              title="Volume"
              value={
                formatLargeNumber(
                  latestHistory.volume
                )
              }
            />

          </div>


          {/* =============================
              PRICE CHART
          ============================== */}

          <div className="card">

            <div className="chart-card-header">

              <div>

                <h3>
                  Price History
                </h3>

                <p>
                  Closing price with
                  moving averages.
                </p>

              </div>

              <BarChart3
                size={21}
              />

            </div>


            <ResponsiveContainer
              width="100%"
              height={420}
            >

              <LineChart
                data={chartData}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#1f354d"
                />


                <XAxis
                  dataKey="date"
                  stroke="#8fa2b8"
                  minTickGap={35}
                />


                <YAxis
                  stroke="#8fa2b8"
                  domain={[
                    "auto",
                    "auto"
                  ]}
                />


                <Tooltip />


                <Legend />


                <Line
                  type="monotone"
                  dataKey="close"
                  name="Close"
                  stroke="#3b82f6"
                  strokeWidth={2.4}
                  dot={false}
                />


                <Line
                  type="monotone"
                  dataKey="ma_20"
                  name="MA 20"
                  stroke="#22c55e"
                  strokeWidth={1.7}
                  dot={false}
                  connectNulls
                />


                <Line
                  type="monotone"
                  dataKey="ma_50"
                  name="MA 50"
                  stroke="#f59e0b"
                  strokeWidth={1.7}
                  dot={false}
                  connectNulls
                />

              </LineChart>

            </ResponsiveContainer>

          </div>


          {/* =============================
              TECHNICAL INDICATORS
          ============================== */}

          {latestIndicator && (

            <>

              <div className="stock-section-title">

                <Activity size={20} />

                <div>
                  <h2>
                    Technical Indicators
                  </h2>

                  <p>
                    Latest calculated market
                    indicators.
                  </p>
                </div>

              </div>


              <div className="indicator-grid">

                <IndicatorCard
                  title="RSI 14"
                  value={
                    formatNumber(
                      latestIndicator.rsi_14,
                      2
                    )
                  }
                  description={
                    getRSIStatus(
                      latestIndicator.rsi_14
                    )
                  }
                />


                <IndicatorCard
                  title="MACD"
                  value={
                    formatNumber(
                      latestIndicator.macd,
                      4
                    )
                  }
                  description="Momentum indicator"
                />


                <IndicatorCard
                  title="MACD Signal"
                  value={
                    formatNumber(
                      latestIndicator.macd_signal,
                      4
                    )
                  }
                  description="MACD signal line"
                />


                <IndicatorCard
                  title="MA 7"
                  value={
                    formatCurrency(
                      latestIndicator.ma_7
                    )
                  }
                  description="7-day moving average"
                />


                <IndicatorCard
                  title="MA 20"
                  value={
                    formatCurrency(
                      latestIndicator.ma_20
                    )
                  }
                  description="20-day moving average"
                />


                <IndicatorCard
                  title="MA 50"
                  value={
                    formatCurrency(
                      latestIndicator.ma_50
                    )
                  }
                  description="50-day moving average"
                />


                <IndicatorCard
                  title="Volatility"
                  value={
                    formatNumber(
                      latestIndicator.volatility_20,
                      4
                    )
                  }
                  description="20-day volatility"
                />


                <IndicatorCard
                  title="Daily Return"
                  value={
                    formatPercentValue(
                      latestIndicator.daily_return
                    )
                  }
                  description="Latest daily return"
                />

              </div>

            </>

          )}


          {/* =============================
              RSI CHART
          ============================== */}

          {indicators.length > 0 && (

            <div className="card">

              <div className="chart-card-header">

                <div>

                  <h3>
                    RSI Analysis
                  </h3>

                  <p>
                    Relative Strength Index
                    for momentum analysis.
                  </p>

                </div>

              </div>


              <ResponsiveContainer
                width="100%"
                height={300}
              >

                <LineChart
                  data={indicators}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#1f354d"
                  />


                  <XAxis
                    dataKey="date"
                    stroke="#8fa2b8"
                    minTickGap={35}
                  />


                  <YAxis
                    stroke="#8fa2b8"
                    domain={[0, 100]}
                  />


                  <Tooltip />


                  <Line
                    type="monotone"
                    dataKey="rsi_14"
                    name="RSI 14"
                    stroke="#8b5cf6"
                    strokeWidth={2}
                    dot={false}
                    connectNulls
                  />

                </LineChart>

              </ResponsiveContainer>


              <div className="rsi-guide">

                <span>
                  Below 30:
                  Oversold
                </span>

                <span>
                  30–70:
                  Neutral
                </span>

                <span>
                  Above 70:
                  Overbought
                </span>

              </div>

            </div>

          )}


          {/* =============================
              RECENT DATA TABLE
          ============================== */}

          <div className="card">

            <h3 className="section-title">
              Recent Historical Data
            </h3>


            <div className="table-wrapper">

              <table>

                <thead>

                  <tr>

                    <th>
                      Date
                    </th>

                    <th>
                      Open
                    </th>

                    <th>
                      High
                    </th>

                    <th>
                      Low
                    </th>

                    <th>
                      Close
                    </th>

                    <th>
                      Volume
                    </th>

                  </tr>

                </thead>


                <tbody>

                  {history
                    .slice(-10)
                    .reverse()
                    .map(
                      (item, index) => (

                        <tr
                          key={
                            item.date ||
                            index
                          }
                        >

                          <td>
                            {item.date}
                          </td>

                          <td>
                            {formatCurrency(
                              item.open
                            )}
                          </td>

                          <td>
                            {formatCurrency(
                              item.high
                            )}
                          </td>

                          <td>
                            {formatCurrency(
                              item.low
                            )}
                          </td>

                          <td>
                            {formatCurrency(
                              item.close
                            )}
                          </td>

                          <td>
                            {formatLargeNumber(
                              item.volume
                            )}
                          </td>

                        </tr>

                      )
                    )}

                </tbody>

              </table>

            </div>

          </div>

        </>

      )}

    </div>
  );
}


/* =========================================
   COMPONENTS
========================================= */

function MetricCard({
  title,
  value,
}) {
  return (
    <div className="stock-metric-card">

      <span>
        {title}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


function IndicatorCard({
  title,
  value,
  description,
}) {
  return (
    <div className="indicator-card">

      <span>
        {title}
      </span>

      <strong>
        {value}
      </strong>

      <small>
        {description}
      </small>

    </div>
  );
}


/* =========================================
   HELPERS
========================================= */

function extractArray(data) {
  if (Array.isArray(data)) {
    return data;
  }

  if (
    Array.isArray(data?.data)
  ) {
    return data.data;
  }

  if (
    Array.isArray(data?.history)
  ) {
    return data.history;
  }

  if (
    Array.isArray(data?.indicators)
  ) {
    return data.indicators;
  }

  return [];
}


function getNumber(value) {
  const number =
    Number(value);

  return Number.isFinite(number)
    ? number
    : null;
}


function formatCurrency(value) {
  const number =
    getNumber(value);

  if (number === null) {
    return "-";
  }

  return `$${number.toFixed(2)}`;
}


function formatNumber(
  value,
  digits = 2
) {
  const number =
    getNumber(value);

  if (number === null) {
    return "-";
  }

  return number.toFixed(
    digits
  );
}


function formatLargeNumber(value) {
  const number =
    getNumber(value);

  if (number === null) {
    return "-";
  }

  return number.toLocaleString(
    "en-US"
  );
}


function formatPercentValue(value) {
  const number =
    getNumber(value);

  if (number === null) {
    return "-";
  }

  return `${(
    number * 100
  ).toFixed(2)}%`;
}


function getRSIStatus(value) {
  const rsi =
    getNumber(value);

  if (rsi === null) {
    return "No RSI data";
  }

  if (rsi > 70) {
    return "Potentially overbought";
  }

  if (rsi < 30) {
    return "Potentially oversold";
  }

  return "Neutral momentum";
}


function mergeChartData(
  history,
  indicators
) {
  const indicatorMap =
    new Map();

  indicators.forEach(
    (item) => {
      indicatorMap.set(
        item.date,
        item
      );
    }
  );


  return history.map(
    (item) => {

      const indicator =
        indicatorMap.get(
          item.date
        ) || {};

      return {
        ...item,

        ma_20:
          indicator.ma_20,

        ma_50:
          indicator.ma_50,
      };

    }
  );
}


export default StockExplorer;