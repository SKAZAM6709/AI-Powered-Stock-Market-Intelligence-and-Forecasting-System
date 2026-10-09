import {
  useEffect,
  useState,
} from "react";

import api from "../api/api";

import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";


function NewsSentiment() {

  const [text, setText] =
    useState(
      "Apple reports strong earnings and higher revenue growth."
    );

  const [model, setModel] =
    useState("finbert");

  const [result, setResult] =
    useState(null);

  const [summary, setSummary] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  useEffect(() => {

    const loadSummary = async () => {

      try {

        const response = await api.get(
          "/sentiment/summary"
        );

        setSummary(
          response.data
        );

      } catch (err) {

        console.error(err);

      }

    };

    loadSummary();

  }, []);


  const analyze = async () => {

    try {

      setLoading(true);
      setError("");

      const response = await api.post(
        "/sentiment/analyze",
        {
          text,
        },
        {
          params: {
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
        "Unable to analyze sentiment."
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
            News Sentiment
          </h1>

          <p>
            Analyze financial news using
            VADER or FinBERT.
          </p>

        </div>

      </div>


      {summary && (

        <div className="stats-grid">

          <SummaryBox
            title="Total Headlines"
            value={
              summary.total_records
            }
          />

          <SummaryBox
            title="Positive"
            value={
              summary.sentiment_counts
                ?.Positive || 0
            }
          />

          <SummaryBox
            title="Neutral"
            value={
              summary.sentiment_counts
                ?.Neutral || 0
            }
          />

          <SummaryBox
            title="Negative"
            value={
              summary.sentiment_counts
                ?.Negative || 0
            }
          />

        </div>
      )}


      <div className="card">

        <div className="form-group">

          <label>
            Financial News Text
          </label>

          <textarea
            rows="5"
            value={text}
            onChange={
              (event) =>
                setText(
                  event.target.value
                )
            }
          />

        </div>


        <div className="sentiment-controls">

          <select
            value={model}
            onChange={
              (event) =>
                setModel(
                  event.target.value
                )
            }
          >

            <option value="vader">
              VADER
            </option>

            <option value="finbert">
              FinBERT
            </option>

          </select>


          <button
            className="primary-button"
            type="button"
            onClick={analyze}
          >
            Analyze Sentiment
          </button>

        </div>

      </div>


      {loading && (
        <Loading
          text="Analyzing sentiment..."
        />
      )}


      {error && (
        <ErrorMessage
          message={error}
        />
      )}


      {result && (

        <div className="card">

          <h2>
            {result.sentiment}
          </h2>

          <p className="muted-text">
            Model: {result.model}
          </p>


          <div className="indicator-grid">

            <SummaryBox
              title="Positive"
              value={result.positive}
            />

            <SummaryBox
              title="Neutral"
              value={result.neutral}
            />

            <SummaryBox
              title="Negative"
              value={result.negative}
            />

            <SummaryBox
              title="Compound"
              value={result.compound}
            />

          </div>

        </div>
      )}

    </div>
  );
}


function SummaryBox({
  title,
  value,
}) {

  return (
    <div className="indicator-card">

      <span>
        {title}
      </span>

      <strong>
        {value ?? "-"}
      </strong>

    </div>
  );
}


export default NewsSentiment;