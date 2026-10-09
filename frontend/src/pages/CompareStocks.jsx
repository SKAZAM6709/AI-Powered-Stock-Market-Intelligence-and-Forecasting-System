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
  Legend,
  ResponsiveContainer,
} from "recharts";

import api from "../api/api";

import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";


function CompareStocks() {

  const [ticker1, setTicker1] =
    useState("AAPL");

  const [ticker2, setTicker2] =
    useState("MSFT");

  const [comparisonData, setComparisonData] =
    useState([]);

  const [summary, setSummary] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  const compareStocks = async () => {

    try {

      setLoading(true);
      setError("");
      setComparisonData([]);
      setSummary(null);


      const symbol1 =
        ticker1.trim().toUpperCase();

      const symbol2 =
        ticker2.trim().toUpperCase();


      if (!symbol1 || !symbol2) {

        setError(
          "Please enter both stock tickers."
        );

        return;
      }


      const [
        response1,
        response2,
      ] = await Promise.all([

        api.get(
          `/stocks/${symbol1}/history?limit=100`
        ),

        api.get(
          `/stocks/${symbol2}/history?limit=100`
        ),

      ]);


      const history1 =
        Array.isArray(response1.data)
          ? response1.data
          : response1.data.data || [];


      const history2 =
        Array.isArray(response2.data)
          ? response2.data
          : response2.data.data || [];


      if (
        history1.length === 0 ||
        history2.length === 0
      ) {

        setError(
          "Historical data was not found for one or both stocks."
        );

        return;
      }


      // =========================================
      // ALIGN DATA BY DATE
      // =========================================

      const stock1Map = {};

      history1.forEach((item) => {

        stock1Map[item.date] =
          Number(item.close);

      });


      const stock2Map = {};

      history2.forEach((item) => {

        stock2Map[item.date] =
          Number(item.close);

      });


      const dates = Object.keys(
        stock1Map
      ).filter(
        (date) =>
          stock2Map[date] !== undefined
      );


      const merged = dates.map(
        (date) => ({
          date,

          [symbol1]:
            stock1Map[date],

          [symbol2]:
            stock2Map[date],
        })
      );


      merged.sort(
        (a, b) =>
          new Date(a.date) -
          new Date(b.date)
      );


      setComparisonData(
        merged
      );


      // =========================================
      // SUMMARY
      // =========================================

      const stock1Start =
        Number(history1[0].close);

      const stock1End =
        Number(
          history1[
            history1.length - 1
          ].close
        );


      const stock2Start =
        Number(history2[0].close);

      const stock2End =
        Number(
          history2[
            history2.length - 1
          ].close
        );


      const stock1Change =
        (
          (
            stock1End -
            stock1Start
          ) /
          stock1Start
        ) * 100;


      const stock2Change =
        (
          (
            stock2End -
            stock2Start
          ) /
          stock2Start
        ) * 100;


      setSummary({

        stock1: {
          ticker: symbol1,
          startPrice:
            stock1Start,
          endPrice:
            stock1End,
          change:
            stock1Change,
        },

        stock2: {
          ticker: symbol2,
          startPrice:
            stock2Start,
          endPrice:
            stock2End,
          change:
            stock2Change,
        },

      });


    } catch (err) {

      console.error(err);

      setError(
        err?.response?.data?.detail ||
        "Unable to compare stocks."
      );

    } finally {

      setLoading(false);

    }

  };


  return (
    <div>

      <div className="page-header">

        <div>

          <h1>
            Compare Stocks
          </h1>

          <p>
            Compare historical performance
            between two stocks.
          </p>

        </div>

      </div>


      {/* =====================================
          INPUTS
      ===================================== */}

      <div className="card compare-form">

        <div className="form-group">

          <label>
            First Stock
          </label>

          <input
            value={ticker1}
            onChange={
              (event) =>
                setTicker1(
                  event.target.value
                )
            }
            placeholder="AAPL"
          />

        </div>


        <div className="form-group">

          <label>
            Second Stock
          </label>

          <input
            value={ticker2}
            onChange={
              (event) =>
                setTicker2(
                  event.target.value
                )
            }
            placeholder="MSFT"
          />

        </div>


        <button
          className="primary-button"
          type="button"
          onClick={compareStocks}
        >
          Compare Stocks
        </button>

      </div>


      {loading && (

        <Loading
          text="Comparing stocks..."
        />

      )}


      {error && (

        <ErrorMessage
          message={error}
        />

      )}


      {/* =====================================
          SUMMARY
      ===================================== */}

      {summary && (

        <div className="comparison-summary">

          <StockSummary
            data={summary.stock1}
          />

          <StockSummary
            data={summary.stock2}
          />

        </div>

      )}


      {/* =====================================
          CHART
      ===================================== */}

      {comparisonData.length > 0 && (

        <div className="card">

          <h3 className="section-title">
            Historical Price Comparison
          </h3>


          <ResponsiveContainer
            width="100%"
            height={400}
          >

            <LineChart
              data={comparisonData}
            >

              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#1f354d"
              />


              <XAxis
                dataKey="date"
                stroke="#8fa2b8"
              />


              <YAxis
                stroke="#8fa2b8"
              />


              <Tooltip />


              <Legend />


              <Line
                type="monotone"
                dataKey={
                  summary.stock1.ticker
                }
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
              />


              <Line
                type="monotone"
                dataKey={
                  summary.stock2.ticker
                }
                stroke="#22c55e"
                strokeWidth={2}
                dot={false}
              />

            </LineChart>

          </ResponsiveContainer>

        </div>

      )}

    </div>
  );
}


function StockSummary({
  data,
}) {

  const positive =
    data.change >= 0;


  return (
    <div className="comparison-card">

      <h2>
        {data.ticker}
      </h2>


      <div className="comparison-price">

        ${data.endPrice.toFixed(2)}

      </div>


      <div
        className={
          positive
            ? "positive-text"
            : "negative-text"
        }
      >

        {positive ? "+" : ""}

        {data.change.toFixed(2)}
        %

      </div>


      <div className="comparison-details">

        <span>
          Start Price
        </span>

        <strong>
          ${data.startPrice.toFixed(2)}
        </strong>

      </div>


      <div className="comparison-details">

        <span>
          Latest Price
        </span>

        <strong>
          ${data.endPrice.toFixed(2)}
        </strong>

      </div>

    </div>
  );
}


export default CompareStocks;