import {
  useState,
} from "react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import api from "../api/api";

import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";


const models = [
  "linear",
  "random_forest",
  "xgboost",
  "arima",
  "lstm",
  "gru",
  "ensemble",
];


function AIForecast() {

  const [ticker, setTicker] =
    useState("AAPL");

  const [horizon, setHorizon] =
    useState(7);

  const [model, setModel] =
    useState("ensemble");

  const [result, setResult] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  const generateForecast = async () => {

    try {

      setLoading(true);
      setError("");
      setResult(null);

      const symbol =
        ticker.trim().toUpperCase();

      const response = await api.get(
        `/forecast/${symbol}`,
        {
          params: {
            horizon,
            model,
          },
        }
      );

      setResult(
        response.data
      );

    } catch (err) {

      console.error(err);

      setError(
        err?.response?.data?.detail ||
        "Unable to generate forecast."
      );

    } finally {

      setLoading(false);

    }

  };


  const forecastChart =
    result?.forecast_series?.map(
      (value, index) => ({
        day: `Day ${index + 1}`,
        price: value,
      })
    ) || [];


  return (
    <div>

      <div className="page-header">

        <div>

          <h1>
            AI Forecast
          </h1>

          <p>
            Forecast prices using ML,
            time-series and deep-learning models.
          </p>

        </div>

      </div>


      <div className="card form-grid">

        <div className="form-group">

          <label>
            Stock
          </label>

          <input
            value={ticker}
            onChange={
              (event) =>
                setTicker(
                  event.target.value
                )
            }
          />

        </div>


        <div className="form-group">

          <label>
            Horizon
          </label>

          <input
            type="number"
            min="1"
            max="30"
            value={horizon}
            onChange={
              (event) =>
                setHorizon(
                  Number(
                    event.target.value
                  )
                )
            }
          />

        </div>


        <div className="form-group">

          <label>
            Model
          </label>

          <select
            value={model}
            onChange={
              (event) =>
                setModel(
                  event.target.value
                )
            }
          >

            {models.map(
              (item) => (
                <option
                  key={item}
                  value={item}
                >
                  {item}
                </option>
              )
            )}

          </select>

        </div>


        <button
          className="primary-button"
          onClick={
            generateForecast
          }
          type="button"
        >
          Generate Forecast
        </button>

      </div>


      {loading && (
        <Loading
          text="Generating forecast..."
        />
      )}


      {error && (
        <ErrorMessage
          message={error}
        />
      )}


      {result && (

        <>

          <div className="forecast-data-grid">

            <ResultBox
              title="Current Price"
              value={`$${result.current_price}`}
            />

            <ResultBox
              title="Predicted Price"
              value={`$${result.predicted_price}`}
            />

            <ResultBox
              title="Expected Change"
              value={`${result.expected_change_pct}%`}
            />

            <ResultBox
              title="Trend"
              value={result.trend}
            />

            <ResultBox
              title="Confidence"
              value={`${result.confidence_pct}%`}
            />

            <ResultBox
              title="Model"
              value={result.model}
            />

          </div>


          {forecastChart.length > 0 && (

            <div className="card">

              <h3 className="section-title">
                Forecast Series
              </h3>

              <ResponsiveContainer
                width="100%"
                height={350}
              >

                <LineChart
                  data={forecastChart}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#1f354d"
                  />

                  <XAxis
                    dataKey="day"
                    stroke="#8fa2b8"
                  />

                  <YAxis
                    stroke="#8fa2b8"
                  />

                  <Tooltip />

                  <Line
                    type="monotone"
                    dataKey="price"
                    stroke="#22c55e"
                    strokeWidth={2}
                  />

                </LineChart>

              </ResponsiveContainer>

            </div>
          )}


          {result.models && (

            <div className="card">

              <h3 className="section-title">
                Ensemble Contributions
              </h3>

              <table>

                <thead>

                  <tr>
                    <th>Model</th>
                    <th>Prediction</th>
                    <th>Weight</th>
                  </tr>

                </thead>

                <tbody>

                  {Object.entries(
                    result.models
                  ).map(
                    ([name, details]) => (
                      <tr key={name}>

                        <td>
                          {name}
                        </td>

                        <td>
                          $
                          {
                            details.predicted_price
                          }
                        </td>

                        <td>
                          {
                            (
                              details.weight *
                              100
                            ).toFixed(0)
                          }
                          %
                        </td>

                      </tr>
                    )
                  )}

                </tbody>

              </table>

            </div>
          )}

        </>
      )}

    </div>
  );
}


function ResultBox({
  title,
  value,
}) {

  return (
    <div className="result-box">

      <span>
        {title}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


export default AIForecast;