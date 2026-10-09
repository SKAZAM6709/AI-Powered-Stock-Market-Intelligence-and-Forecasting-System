function About() {
  return (
    <div>

      <div className="page-header">

        <div>

          <h1>
            About StockAI
          </h1>

          <p>
            AI-powered stock market intelligence
            and forecasting platform.
          </p>

        </div>

      </div>


      <div className="card about-card">

        <h2>
          Project Overview
        </h2>

        <p>
          StockAI combines historical stock-market
          analysis, machine learning, deep learning,
          time-series forecasting and financial
          news sentiment analysis.
        </p>


        <h3>
          Forecasting Models
        </h3>

        <p>
          Linear Regression, Random Forest,
          XGBoost, ARIMA, LSTM, GRU and
          Weighted Ensemble.
        </p>


        <h3>
          NLP Models
        </h3>

        <p>
          VADER and FinBERT.
        </p>


        <h3>
          Technology Stack
        </h3>

        <p>
          Python, FastAPI, Pandas,
          Scikit-learn, XGBoost,
          TensorFlow/Keras, PyTorch,
          Transformers, React, Vite,
          Axios and Recharts.
        </p>

      </div>

    </div>
  );
}


export default About;