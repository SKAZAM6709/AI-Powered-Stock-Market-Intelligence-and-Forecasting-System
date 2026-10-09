import {
  useEffect,
  useState,
} from "react";

import {
  TrendingUp,
  TrendingDown,
  BrainCircuit,
  Newspaper,
} from "lucide-react";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import api from "../api/api";

import StatCard from "../components/StatCard";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";


function Dashboard() {

  const [market, setMarket] =
    useState(null);

  const [sentiment, setSentiment] =
    useState(null);

  const [analytics, setAnalytics] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  useEffect(() => {

    const loadDashboard = async () => {

      try {

        setLoading(true);
        setError("");

        const [
          marketResponse,
          sentimentResponse,
          analyticsResponse,
        ] = await Promise.all([
          api.get(
            "/market/overview?limit=5"
          ),

          api.get(
            "/sentiment/summary"
          ),

          api.get(
            "/analytics/overview"
          ),
        ]);

        setMarket(
          marketResponse.data
        );

        setSentiment(
          sentimentResponse.data
        );

        setAnalytics(
          analyticsResponse.data
        );

      } catch (err) {

        console.error(err);

        setError(
          "Unable to load dashboard. Make sure the FastAPI backend is running."
        );

      } finally {

        setLoading(false);

      }

    };

    loadDashboard();

  }, []);


  if (loading) {
    return (
      <Loading
        text="Loading dashboard..."
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


  const counts =
    sentiment?.sentiment_counts || {};


  const chartData = [
    {
      name: "Positive",
      value:
        counts.Positive ||
        counts.positive ||
        0,
    },
    {
      name: "Neutral",
      value:
        counts.Neutral ||
        counts.neutral ||
        0,
    },
    {
      name: "Negative",
      value:
        counts.Negative ||
        counts.negative ||
        0,
    },
  ];


  return (
    <div>

      <div className="page-header">

        <div>

          <h1>
            Dashboard
          </h1>

          <p>
            Market intelligence, AI forecasting,
            and financial-news sentiment overview.
          </p>

        </div>

      </div>


      <div className="stats-grid">

        <StatCard
          title="Top Gainers"
          value={
            market?.top_gainers?.length || 0
          }
          subtitle="Leading stocks"
          icon={TrendingUp}
        />

        <StatCard
          title="Top Losers"
          value={
            market?.top_losers?.length || 0
          }
          subtitle="Largest declines"
          icon={TrendingDown}
        />

        <StatCard
          title="News Headlines"
          value={
            sentiment?.total_records || 0
          }
          subtitle="Analyzed by NLP"
          icon={Newspaper}
        />

        <StatCard
          title="ML Models"
          value={
            analytics?.total_models || 0
          }
          subtitle="Forecasting models"
          icon={BrainCircuit}
        />

      </div>


      <div className="dashboard-grid">

        <div className="card">

          <h3 className="section-title">
            Market Leaders
          </h3>


          <div className="market-columns">

            <div>

              <h4>
                Top Gainers
              </h4>

              {market?.top_gainers?.map(
                (stock, index) => (
                  <div
                    className="market-row"
                    key={
                      stock.ticker ||
                      stock.Name ||
                      index
                    }
                  >

                    <strong>
                      {stock.ticker ||
                        stock.Name}
                    </strong>

                    <span className="positive-text">
                      +
                      {stock.change_pct}
                      %
                    </span>

                  </div>
                )
              )}

            </div>


            <div>

              <h4>
                Top Losers
              </h4>

              {market?.top_losers?.map(
                (stock, index) => (
                  <div
                    className="market-row"
                    key={
                      stock.ticker ||
                      stock.Name ||
                      index
                    }
                  >

                    <strong>
                      {stock.ticker ||
                        stock.Name}
                    </strong>

                    <span className="negative-text">
                      {stock.change_pct}
                      %
                    </span>

                  </div>
                )
              )}

            </div>

          </div>

        </div>


        <div className="card">

          <h3 className="section-title">
            News Sentiment Distribution
          </h3>


          <ResponsiveContainer
            width="100%"
            height={300}
          >

            <BarChart
              data={chartData}
            >

              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#1f354d"
              />

              <XAxis
                dataKey="name"
                stroke="#8fa2b8"
              />

              <YAxis
                stroke="#8fa2b8"
              />

              <Tooltip />

              <Bar
                dataKey="value"
                fill="#3b82f6"
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

      </div>

    </div>
  );
}


export default Dashboard;