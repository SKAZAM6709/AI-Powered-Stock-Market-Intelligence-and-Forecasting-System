import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

import {
  BrainCircuit,
  Trophy,
  Target,
  Newspaper,
} from "lucide-react";

import api from "../api/api";

import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";
import StatCard from "../components/StatCard";


function ModelAnalytics() {

  const [
    modelMetrics,
    setModelMetrics
  ] = useState(null);

  const [
    bestModels,
    setBestModels
  ] = useState(null);

  const [
    sentimentMetrics,
    setSentimentMetrics
  ] = useState(null);

  const [
    loading,
    setLoading
  ] = useState(true);

  const [
    error,
    setError
  ] = useState("");


  useEffect(() => {

    const loadAnalytics = async () => {

      try {

        setLoading(true);
        setError("");


        const [
          modelsResponse,
          bestResponse,
          sentimentResponse,
        ] = await Promise.all([

          api.get(
            "/analytics/models"
          ),

          api.get(
            "/analytics/best-models"
          ),

          api.get(
            "/analytics/sentiment/models"
          ),

        ]);


        setModelMetrics(
          modelsResponse.data
        );

        setBestModels(
          bestResponse.data
        );

        setSentimentMetrics(
          sentimentResponse.data
        );


      } catch (err) {

        console.error(
          "Analytics loading error:",
          err
        );

        setError(
          err?.response?.data?.detail ||
          "Unable to load model analytics. Make sure FastAPI is running."
        );

      } finally {

        setLoading(false);

      }

    };


    loadAnalytics();

  }, []);


  const forecastingData =
    useMemo(() => {

      if (!modelMetrics) {
        return [];
      }


      const models =
        modelMetrics.models ||
        modelMetrics;


      if (
        !models ||
        typeof models !== "object"
      ) {
        return [];
      }


      return Object.entries(
        models
      ).map(
        ([name, metrics]) => ({

          model:
            formatModelName(name),

          mae:
            safeNumber(
              metrics?.mae
            ),

          rmse:
            safeNumber(
              metrics?.rmse
            ),

          r2:
            safeNumber(
              metrics?.r2
            ),

        })
      );

    }, [modelMetrics]);


  const sentimentChartData = [

    {
      model: "VADER",

      accuracy:
        safeNumber(
          sentimentMetrics
            ?.vader_accuracy_pct
        ),
    },

    {
      model: "FinBERT",

      accuracy:
        safeNumber(
          sentimentMetrics
            ?.finbert_accuracy_pct
        ),
    },

  ];


  if (loading) {

    return (
      <Loading
        text="Loading model analytics..."
      />
    );

  }


  if (error) {

    return (
      <ErrorMessage
        message={error}
      />
    );

  }


  return (

    <div>

      {/* =============================
          HEADER
      ============================== */}

      <div className="page-header">

        <div>

          <h1>
            Model Analytics
          </h1>

          <p>
            Evaluate forecasting models
            and financial sentiment models.
          </p>

        </div>

      </div>


      {/* =============================
          FORECAST SUMMARY
      ============================== */}

      <div className="analytics-section-header">

        <div>

          <h2>
            Forecasting Models
          </h2>

          <p>
            Machine-learning model
            performance comparison.
          </p>

        </div>

      </div>


      <div className="stats-grid">

        <StatCard
          title="Best MAE"
          value={
            getBestValue(
              bestModels,
              [
                "best_mae",
                "mae"
              ]
            )
          }
          subtitle="Lowest prediction error"
          icon={Target}
        />


        <StatCard
          title="Best RMSE"
          value={
            getBestValue(
              bestModels,
              [
                "best_rmse",
                "rmse"
              ]
            )
          }
          subtitle="Lowest root mean square error"
          icon={BrainCircuit}
        />


        <StatCard
          title="Best R²"
          value={
            getBestValue(
              bestModels,
              [
                "best_r2",
                "r2"
              ]
            )
          }
          subtitle="Highest goodness of fit"
          icon={Trophy}
        />


        <StatCard
          title="Models Evaluated"
          value={
            forecastingData.length
          }
          subtitle="Machine learning models"
          icon={BrainCircuit}
        />

      </div>


      {/* =============================
          FORECASTING TABLE
      ============================== */}

      <div className="card">

        <h3 className="section-title">
          Forecasting Model Metrics
        </h3>


        {forecastingData.length === 0 ? (

          <p className="muted-text">
            No forecasting metrics were
            returned by the backend.
          </p>

        ) : (

          <div className="table-wrapper">

            <table>

              <thead>

                <tr>

                  <th>
                    Model
                  </th>

                  <th>
                    MAE
                  </th>

                  <th>
                    RMSE
                  </th>

                  <th>
                    R²
                  </th>

                </tr>

              </thead>


              <tbody>

                {forecastingData.map(
                  (item) => (

                    <tr key={item.model}>

                      <td>
                        <strong>
                          {item.model}
                        </strong>
                      </td>

                      <td>
                        {formatMetric(
                          item.mae
                        )}
                      </td>

                      <td>
                        {formatMetric(
                          item.rmse
                        )}
                      </td>

                      <td>
                        {formatMetric(
                          item.r2,
                          4
                        )}
                      </td>

                    </tr>

                  )
                )}

              </tbody>

            </table>

          </div>

        )}

      </div>


      {/* =============================
          ERROR CHART
      ============================== */}

      {forecastingData.length > 0 && (

        <div className="card">

          <h3 className="section-title">
            Forecasting Error Comparison
          </h3>


          <ResponsiveContainer
            width="100%"
            height={360}
          >

            <BarChart
              data={forecastingData}
            >

              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#1f354d"
              />


              <XAxis
                dataKey="model"
                stroke="#8fa2b8"
              />


              <YAxis
                stroke="#8fa2b8"
              />


              <Tooltip />


              <Legend />


              <Bar
                dataKey="mae"
                name="MAE"
                fill="#3b82f6"
                radius={[
                  5,
                  5,
                  0,
                  0
                ]}
              />


              <Bar
                dataKey="rmse"
                name="RMSE"
                fill="#06b6d4"
                radius={[
                  5,
                  5,
                  0,
                  0
                ]}
              />

            </BarChart>

          </ResponsiveContainer>

        </div>

      )}


      {/* =============================
          R2 CHART
      ============================== */}

      {forecastingData.length > 0 && (

        <div className="card">

          <h3 className="section-title">
            R² Score Comparison
          </h3>


          <ResponsiveContainer
            width="100%"
            height={340}
          >

            <BarChart
              data={forecastingData}
            >

              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#1f354d"
              />


              <XAxis
                dataKey="model"
                stroke="#8fa2b8"
              />


              <YAxis
                stroke="#8fa2b8"
                domain={[0, 1]}
              />


              <Tooltip />


              <Bar
                dataKey="r2"
                name="R²"
                fill="#22c55e"
                radius={[
                  6,
                  6,
                  0,
                  0
                ]}
              />

            </BarChart>

          </ResponsiveContainer>

        </div>

      )}


      {/* =============================
          SENTIMENT ANALYTICS
      ============================== */}

      <div className="analytics-section-header">

        <div>

          <h2>
            Sentiment Models
          </h2>

          <p>
            Comparison of VADER and
            FinBERT against dataset labels.
          </p>

        </div>

      </div>


      <div className="stats-grid">

        <StatCard
          title="VADER Accuracy"
          value={
            `${formatPercent(
              sentimentMetrics
                ?.vader_accuracy_pct
            )}%`
          }
          subtitle="Lexicon-based sentiment"
          icon={Newspaper}
        />


        <StatCard
          title="FinBERT Accuracy"
          value={
            `${formatPercent(
              sentimentMetrics
                ?.finbert_accuracy_pct
            )}%`
          }
          subtitle="Transformer sentiment model"
          icon={BrainCircuit}
        />


        <StatCard
          title="Model Agreement"
          value={
            `${formatPercent(
              sentimentMetrics
                ?.agreement_pct
            )}%`
          }
          subtitle="VADER / FinBERT agreement"
          icon={Target}
        />


        <StatCard
          title="Best Model"
          value={
            sentimentMetrics
              ?.best_model ||
            "-"
          }
          subtitle="Highest label agreement"
          icon={Trophy}
        />

      </div>


      {/* =============================
          SENTIMENT CHART
      ============================== */}

      <div className="card">

        <h3 className="section-title">
          Sentiment Accuracy Comparison
        </h3>


        <ResponsiveContainer
          width="100%"
          height={350}
        >

          <BarChart
            data={
              sentimentChartData
            }
          >

            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#1f354d"
            />


            <XAxis
              dataKey="model"
              stroke="#8fa2b8"
            />


            <YAxis
              stroke="#8fa2b8"
              domain={[
                0,
                100
              ]}
            />


            <Tooltip />


            <Bar
              dataKey="accuracy"
              name="Accuracy (%)"
              fill="#8b5cf6"
              radius={[
                6,
                6,
                0,
                0
              ]}
            />

          </BarChart>

        </ResponsiveContainer>

      </div>


      {/* =============================
          SENTIMENT TABLE
      ============================== */}

      <div className="card">

        <h3 className="section-title">
          Sentiment Evaluation Summary
        </h3>


        <div className="table-wrapper">

          <table>

            <thead>

              <tr>

                <th>
                  Metric
                </th>

                <th>
                  Value
                </th>

              </tr>

            </thead>


            <tbody>

              <tr>

                <td>
                  Total Records
                </td>

                <td>
                  {
                    sentimentMetrics
                      ?.total_records ??
                    "-"
                  }
                </td>

              </tr>


              <tr>

                <td>
                  VADER Accuracy
                </td>

                <td>
                  {
                    formatPercent(
                      sentimentMetrics
                        ?.vader_accuracy_pct
                    )
                  }
                  %
                </td>

              </tr>


              <tr>

                <td>
                  FinBERT Accuracy
                </td>

                <td>
                  {
                    formatPercent(
                      sentimentMetrics
                        ?.finbert_accuracy_pct
                    )
                  }
                  %
                </td>

              </tr>


              <tr>

                <td>
                  VADER / FinBERT Agreement
                </td>

                <td>
                  {
                    formatPercent(
                      sentimentMetrics
                        ?.agreement_pct
                    )
                  }
                  %
                </td>

              </tr>


              <tr>

                <td>
                  Best Sentiment Model
                </td>

                <td>
                  {
                    sentimentMetrics
                      ?.best_model ||
                    "-"
                  }
                </td>

              </tr>

            </tbody>

          </table>

        </div>

      </div>


      <div className="analytics-note">

        <strong>
          Evaluation Note:
        </strong>

        <span>
          Forecasting metrics evaluate
          historical prediction error.
          Sentiment accuracy represents
          agreement with the labeled
          financial-news dataset.
        </span>

      </div>

    </div>
  );
}


/* =========================================
   HELPERS
========================================= */

function safeNumber(value) {

  const number =
    Number(value);

  return Number.isFinite(number)
    ? number
    : 0;
}


function formatMetric(
  value,
  digits = 3
) {

  const number =
    Number(value);

  if (!Number.isFinite(number)) {
    return "-";
  }

  return number.toFixed(
    digits
  );
}


function formatPercent(value) {

  const number =
    Number(value);

  if (!Number.isFinite(number)) {
    return "0.00";
  }

  return number.toFixed(2);
}


function formatModelName(name) {

  return String(name)
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase()
    );
}


function getBestValue(
  data,
  keys
) {

  if (!data) {
    return "-";
  }


  for (
    const key of keys
  ) {

    const value =
      data[key];


    if (
      typeof value === "string"
    ) {

      return formatModelName(
        value
      );

    }


    if (
      value &&
      typeof value === "object"
    ) {

      if (value.model) {

        return formatModelName(
          value.model
        );

      }

      if (value.name) {

        return formatModelName(
          value.name
        );

      }

    }

  }


  return "-";
}


export default ModelAnalytics;