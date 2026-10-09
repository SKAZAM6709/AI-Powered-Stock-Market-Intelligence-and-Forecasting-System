import math
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from keras.models import load_model
from sklearn.linear_model import LinearRegression

from .stock_service import get_stock_history

from ..ml.preprocessing.feature_engineering import (
    build_features,
)

from ..ml.forecasting.arima_model import (
    forecast_with_arima,
)

from ..ml.forecasting.ensemble import (
    get_ensemble_weights,
    weighted_average,
)


# =================================================
# PROJECT PATHS
# =================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]


# =================================================
# MACHINE LEARNING MODEL PATHS
# =================================================

ML_MODEL_DIR = (
    PROJECT_ROOT
    / "models"
    / "machine_learning"
)


RF_MODEL_PATH = (
    ML_MODEL_DIR
    / "random_forest.joblib"
)


XGB_MODEL_PATH = (
    ML_MODEL_DIR
    / "xgboost.joblib"
)


FEATURES_PATH = (
    ML_MODEL_DIR
    / "feature_columns.joblib"
)


# =================================================
# DEEP LEARNING MODEL PATHS
# =================================================

LSTM_MODEL_ROOT = (
    PROJECT_ROOT
    / "models"
    / "time_series"
    / "lstm"
)


GRU_MODEL_ROOT = (
    PROJECT_ROOT
    / "models"
    / "time_series"
    / "gru"
)


# =================================================
# HELPER FUNCTIONS
# =================================================

def get_trend(
    change: float
) -> str:

    if change > 0:
        return "Bullish"

    if change < 0:
        return "Bearish"

    return "Neutral"


def calculate_confidence(
    stock: pd.DataFrame,
    horizon: int
) -> tuple[float, float]:

    returns = (
        stock["close"]
        .pct_change()
        .dropna()
    )

    if len(returns) > 0:

        volatility = float(
            returns.std()
        )

    else:

        volatility = 0.0

    confidence = (
        0.90
        - volatility
        * math.sqrt(horizon)
        * 2
    )

    confidence = max(
        0.50,
        min(
            0.95,
            confidence
        )
    )

    return (
        volatility,
        confidence
    )


# =================================================
# LINEAR REGRESSION
# =================================================

def forecast_linear(
    ticker: str,
    horizon: int = 7
) -> dict:

    ticker = (
        ticker
        .strip()
        .upper()
    )

    horizon = max(
        1,
        min(
            int(horizon),
            60
        )
    )

    stock = get_stock_history(
        ticker=ticker,
        limit=180
    )

    if len(stock) < 30:

        raise ValueError(
            f"Not enough historical data for {ticker}."
        )

    prices = (
        stock["close"]
        .to_numpy(
            dtype=float
        )
    )

    x = np.arange(
        len(prices)
    ).reshape(
        -1,
        1
    )

    training_window = min(
        60,
        len(prices)
    )

    x_train = x[
        -training_window:
    ]

    y_train = prices[
        -training_window:
    ]

    model = LinearRegression()

    model.fit(
        x_train,
        y_train
    )

    future_position = (
        len(prices)
        - 1
        + horizon
    )

    future_x = np.array(
        [
            [
                future_position
            ]
        ]
    )

    predicted_price = float(
        model.predict(
            future_x
        )[0]
    )

    current_price = float(
        prices[-1]
    )

    predicted_price = max(
        predicted_price,
        0.01
    )

    expected_change = (
        predicted_price
        - current_price
    )

    expected_change_pct = (
        expected_change
        / current_price
        * 100
        if current_price != 0
        else 0.0
    )

    volatility, confidence = (
        calculate_confidence(
            stock,
            horizon
        )
    )

    return {
        "ticker": ticker,

        "forecast_horizon_days":
            horizon,

        "current_price":
            round(
                current_price,
                2
            ),

        "predicted_price":
            round(
                predicted_price,
                2
            ),

        "expected_change":
            round(
                expected_change,
                2
            ),

        "expected_change_pct":
            round(
                expected_change_pct,
                2
            ),

        "trend":
            get_trend(
                expected_change
            ),

        "volatility":
            round(
                volatility,
                6
            ),

        "confidence":
            round(
                confidence,
                4
            ),

        "confidence_pct":
            round(
                confidence * 100,
                2
            ),

        "model":
            "Linear Regression Baseline"
    }


# =================================================
# RANDOM FOREST
# =================================================

def forecast_random_forest(
    ticker: str
) -> dict:

    ticker = (
        ticker
        .strip()
        .upper()
    )

    if not RF_MODEL_PATH.exists():

        raise FileNotFoundError(
            "Random Forest model not found. "
            "Run scripts/train_ml_models.py first."
        )

    if not FEATURES_PATH.exists():

        raise FileNotFoundError(
            "Feature columns file not found."
        )

    model = joblib.load(
        RF_MODEL_PATH
    )

    feature_columns = joblib.load(
        FEATURES_PATH
    )

    stock = get_stock_history(
        ticker=ticker,
        limit=120
    )

    if len(stock) < 60:

        raise ValueError(
            f"Not enough historical data for {ticker}."
        )

    featured = build_features(
        stock,
        forecast_horizon=1
    )

    latest = (
        featured
        .dropna(
            subset=feature_columns
        )
        .tail(1)
    )

    if latest.empty:

        raise ValueError(
            f"Could not build ML features for {ticker}."
        )

    X_latest = latest[
        feature_columns
    ]

    predicted_price = float(
        model.predict(
            X_latest
        )[0]
    )

    current_price = float(
        stock.iloc[-1]["close"]
    )

    predicted_price = max(
        predicted_price,
        0.01
    )

    expected_change = (
        predicted_price
        - current_price
    )

    expected_change_pct = (
        expected_change
        / current_price
        * 100
        if current_price != 0
        else 0.0
    )

    volatility, confidence = (
        calculate_confidence(
            stock,
            1
        )
    )

    return {
        "ticker":
            ticker,

        "forecast_horizon_days":
            1,

        "current_price":
            round(
                current_price,
                2
            ),

        "predicted_price":
            round(
                predicted_price,
                2
            ),

        "expected_change":
            round(
                expected_change,
                2
            ),

        "expected_change_pct":
            round(
                expected_change_pct,
                2
            ),

        "trend":
            get_trend(
                expected_change
            ),

        "volatility":
            round(
                volatility,
                6
            ),

        "confidence":
            round(
                confidence,
                4
            ),

        "confidence_pct":
            round(
                confidence * 100,
                2
            ),

        "model":
            "Random Forest"
    }


# =================================================
# XGBOOST
# =================================================

def forecast_xgboost(
    ticker: str
) -> dict:

    ticker = (
        ticker
        .strip()
        .upper()
    )

    if not XGB_MODEL_PATH.exists():

        raise FileNotFoundError(
            "XGBoost model not found. "
            "Run scripts/train_ml_models.py first."
        )

    if not FEATURES_PATH.exists():

        raise FileNotFoundError(
            "Feature columns file not found."
        )

    model = joblib.load(
        XGB_MODEL_PATH
    )

    feature_columns = joblib.load(
        FEATURES_PATH
    )

    stock = get_stock_history(
        ticker=ticker,
        limit=120
    )

    if len(stock) < 60:

        raise ValueError(
            f"Not enough historical data for {ticker}."
        )

    featured = build_features(
        stock,
        forecast_horizon=1
    )

    latest = (
        featured
        .dropna(
            subset=feature_columns
        )
        .tail(1)
    )

    if latest.empty:

        raise ValueError(
            f"Could not build ML features for {ticker}."
        )

    X_latest = latest[
        feature_columns
    ]

    predicted_price = float(
        model.predict(
            X_latest
        )[0]
    )

    current_price = float(
        stock.iloc[-1]["close"]
    )

    predicted_price = max(
        predicted_price,
        0.01
    )

    expected_change = (
        predicted_price
        - current_price
    )

    expected_change_pct = (
        expected_change
        / current_price
        * 100
        if current_price != 0
        else 0.0
    )

    volatility, confidence = (
        calculate_confidence(
            stock,
            1
        )
    )

    return {
        "ticker":
            ticker,

        "forecast_horizon_days":
            1,

        "current_price":
            round(
                current_price,
                2
            ),

        "predicted_price":
            round(
                predicted_price,
                2
            ),

        "expected_change":
            round(
                expected_change,
                2
            ),

        "expected_change_pct":
            round(
                expected_change_pct,
                2
            ),

        "trend":
            get_trend(
                expected_change
            ),

        "volatility":
            round(
                volatility,
                6
            ),

        "confidence":
            round(
                confidence,
                4
            ),

        "confidence_pct":
            round(
                confidence * 100,
                2
            ),

        "model":
            "XGBoost"
    }


# =================================================
# ARIMA
# =================================================

def forecast_arima(
    ticker: str,
    horizon: int = 7
) -> dict:

    ticker = (
        ticker
        .strip()
        .upper()
    )

    horizon = max(
        1,
        min(
            int(horizon),
            60
        )
    )

    stock = get_stock_history(
        ticker=ticker,
        limit=250
    )

    if len(stock) < 30:

        raise ValueError(
            f"Not enough historical data for {ticker}."
        )

    prices = (
        stock["close"]
        .astype(float)
    )

    forecast_values = (
        forecast_with_arima(
            prices=prices,
            horizon=horizon
        )
    )

    forecast_list = [
        float(value)
        for value in forecast_values
    ]

    if not forecast_list:

        raise ValueError(
            f"ARIMA returned no forecast for {ticker}."
        )

    predicted_price = float(
        forecast_list[-1]
    )

    current_price = float(
        prices.iloc[-1]
    )

    predicted_price = max(
        predicted_price,
        0.01
    )

    expected_change = (
        predicted_price
        - current_price
    )

    expected_change_pct = (
        expected_change
        / current_price
        * 100
        if current_price != 0
        else 0.0
    )

    volatility, confidence = (
        calculate_confidence(
            stock,
            horizon
        )
    )

    return {
        "ticker":
            ticker,

        "forecast_horizon_days":
            horizon,

        "current_price":
            round(
                current_price,
                2
            ),

        "predicted_price":
            round(
                predicted_price,
                2
            ),

        "expected_change":
            round(
                expected_change,
                2
            ),

        "expected_change_pct":
            round(
                expected_change_pct,
                2
            ),

        "trend":
            get_trend(
                expected_change
            ),

        "volatility":
            round(
                volatility,
                6
            ),

        "confidence":
            round(
                confidence,
                4
            ),

        "confidence_pct":
            round(
                confidence * 100,
                2
            ),

        "forecast_series": [
            round(
                value,
                2
            )
            for value in forecast_list
        ],

        "model":
            "ARIMA (5,1,0)"
    }


# =================================================
# LSTM
# =================================================

def forecast_lstm(
    ticker: str,
    horizon: int = 7
) -> dict:

    ticker = (
        ticker
        .strip()
        .upper()
    )

    horizon = max(
        1,
        min(
            int(horizon),
            30
        )
    )

    ticker_model_dir = (
        LSTM_MODEL_ROOT
        / ticker
    )

    model_path = (
        ticker_model_dir
        / "lstm_model.keras"
    )

    scaler_path = (
        ticker_model_dir
        / "scaler.joblib"
    )

    if not model_path.exists():

        raise FileNotFoundError(
            f"LSTM model not found for {ticker}. "
            f"Train it using: "
            f"python scripts/train_lstm.py "
            f"--ticker {ticker} --epochs 30"
        )

    if not scaler_path.exists():

        raise FileNotFoundError(
            f"LSTM scaler not found for {ticker}."
        )

    model = load_model(
        model_path
    )

    scaler = joblib.load(
        scaler_path
    )

    stock = get_stock_history(
        ticker=ticker,
        limit=120
    )

    if len(stock) < 60:

        raise ValueError(
            f"Not enough historical data "
            f"for LSTM forecast: {ticker}."
        )

    prices = (
        stock["close"]
        .to_numpy(
            dtype=np.float32
        )
        .reshape(
            -1,
            1
        )
    )

    current_price = float(
        prices[-1][0]
    )

    scaled_prices = scaler.transform(
        prices
    )

    sequence = (
        scaled_prices[
            -60:
        ]
        .flatten()
        .tolist()
    )

    forecast_prices = []

    for _ in range(
        horizon
    ):

        input_sequence = np.array(
            sequence[-60:],
            dtype=np.float32
        )

        input_sequence = (
            input_sequence
            .reshape(
                1,
                60,
                1
            )
        )

        prediction = model.predict(
            input_sequence,
            verbose=0
        )

        predicted_scaled = float(
            prediction[0][0]
        )

        predicted_price = float(
            scaler.inverse_transform(
                np.array(
                    [
                        [
                            predicted_scaled
                        ]
                    ]
                )
            )[0][0]
        )

        predicted_price = max(
            predicted_price,
            0.01
        )

        forecast_prices.append(
            predicted_price
        )

        sequence.append(
            predicted_scaled
        )

    final_predicted_price = float(
        forecast_prices[-1]
    )

    expected_change = (
        final_predicted_price
        - current_price
    )

    expected_change_pct = (
        expected_change
        / current_price
        * 100
        if current_price != 0
        else 0.0
    )

    volatility, confidence = (
        calculate_confidence(
            stock,
            horizon
        )
    )

    return {
        "ticker":
            ticker,

        "forecast_horizon_days":
            horizon,

        "current_price":
            round(
                current_price,
                2
            ),

        "predicted_price":
            round(
                final_predicted_price,
                2
            ),

        "expected_change":
            round(
                expected_change,
                2
            ),

        "expected_change_pct":
            round(
                expected_change_pct,
                2
            ),

        "trend":
            get_trend(
                expected_change
            ),

        "volatility":
            round(
                volatility,
                6
            ),

        "confidence":
            round(
                confidence,
                4
            ),

        "confidence_pct":
            round(
                confidence * 100,
                2
            ),

        "forecast_series": [
            round(
                value,
                2
            )
            for value in forecast_prices
        ],

        "model":
            "LSTM"
    }


# =================================================
# GRU
# =================================================

def forecast_gru(
    ticker: str,
    horizon: int = 7
) -> dict:

    ticker = (
        ticker
        .strip()
        .upper()
    )

    horizon = max(
        1,
        min(
            int(horizon),
            30
        )
    )

    ticker_model_dir = (
        GRU_MODEL_ROOT
        / ticker
    )

    model_path = (
        ticker_model_dir
        / "gru_model.keras"
    )

    scaler_path = (
        ticker_model_dir
        / "scaler.joblib"
    )

    if not model_path.exists():

        raise FileNotFoundError(
            f"GRU model not found for {ticker}. "
            f"Train it using: "
            f"python scripts/train_gru.py "
            f"--ticker {ticker} --epochs 30"
        )

    if not scaler_path.exists():

        raise FileNotFoundError(
            f"GRU scaler not found for {ticker}."
        )

    model = load_model(
        model_path
    )

    scaler = joblib.load(
        scaler_path
    )

    stock = get_stock_history(
        ticker=ticker,
        limit=120
    )

    if len(stock) < 60:

        raise ValueError(
            f"Not enough historical data "
            f"for GRU forecast: {ticker}."
        )

    prices = (
        stock["close"]
        .to_numpy(
            dtype=np.float32
        )
        .reshape(
            -1,
            1
        )
    )

    current_price = float(
        prices[-1][0]
    )

    scaled_prices = scaler.transform(
        prices
    )

    sequence = (
        scaled_prices[
            -60:
        ]
        .flatten()
        .tolist()
    )

    forecast_prices = []

    for _ in range(
        horizon
    ):

        input_sequence = np.array(
            sequence[-60:],
            dtype=np.float32
        )

        input_sequence = (
            input_sequence
            .reshape(
                1,
                60,
                1
            )
        )

        prediction = model.predict(
            input_sequence,
            verbose=0
        )

        predicted_scaled = float(
            prediction[0][0]
        )

        predicted_price = float(
            scaler.inverse_transform(
                np.array(
                    [
                        [
                            predicted_scaled
                        ]
                    ]
                )
            )[0][0]
        )

        predicted_price = max(
            predicted_price,
            0.01
        )

        forecast_prices.append(
            predicted_price
        )

        sequence.append(
            predicted_scaled
        )

    final_predicted_price = float(
        forecast_prices[-1]
    )

    expected_change = (
        final_predicted_price
        - current_price
    )

    expected_change_pct = (
        expected_change
        / current_price
        * 100
        if current_price != 0
        else 0.0
    )

    volatility, confidence = (
        calculate_confidence(
            stock,
            horizon
        )
    )

    return {
        "ticker":
            ticker,

        "forecast_horizon_days":
            horizon,

        "current_price":
            round(
                current_price,
                2
            ),

        "predicted_price":
            round(
                final_predicted_price,
                2
            ),

        "expected_change":
            round(
                expected_change,
                2
            ),

        "expected_change_pct":
            round(
                expected_change_pct,
                2
            ),

        "trend":
            get_trend(
                expected_change
            ),

        "volatility":
            round(
                volatility,
                6
            ),

        "confidence":
            round(
                confidence,
                4
            ),

        "confidence_pct":
            round(
                confidence * 100,
                2
            ),

        "forecast_series": [
            round(
                value,
                2
            )
            for value in forecast_prices
        ],

        "model":
            "GRU"
    }


# =================================================
# ENSEMBLE
# =================================================

def forecast_ensemble(
    ticker: str,
    horizon: int = 7
) -> dict:

    ticker = (
        ticker
        .strip()
        .upper()
    )

    horizon = max(
        1,
        min(
            int(horizon),
            30
        )
    )

    weights = get_ensemble_weights(
        horizon
    )

    predictions = {}

    model_details = {}


    # -------------------------------------------------
    # Linear Regression
    # -------------------------------------------------

    linear_result = forecast_linear(
        ticker=ticker,
        horizon=horizon
    )

    predictions[
        "linear"
    ] = linear_result[
        "predicted_price"
    ]

    model_details[
        "linear"
    ] = {
        "predicted_price":
            linear_result[
                "predicted_price"
            ],

        "weight":
            weights.get(
                "linear",
                0.0
            )
    }


    # -------------------------------------------------
    # ARIMA
    # -------------------------------------------------

    arima_result = forecast_arima(
        ticker=ticker,
        horizon=horizon
    )

    predictions[
        "arima"
    ] = arima_result[
        "predicted_price"
    ]

    model_details[
        "arima"
    ] = {
        "predicted_price":
            arima_result[
                "predicted_price"
            ],

        "weight":
            weights.get(
                "arima",
                0.0
            )
    }


    # -------------------------------------------------
    # LSTM
    # -------------------------------------------------

    lstm_result = forecast_lstm(
        ticker=ticker,
        horizon=horizon
    )

    predictions[
        "lstm"
    ] = lstm_result[
        "predicted_price"
    ]

    model_details[
        "lstm"
    ] = {
        "predicted_price":
            lstm_result[
                "predicted_price"
            ],

        "weight":
            weights.get(
                "lstm",
                0.0
            )
    }


    # -------------------------------------------------
    # GRU
    # -------------------------------------------------

    gru_result = forecast_gru(
        ticker=ticker,
        horizon=horizon
    )

    predictions[
        "gru"
    ] = gru_result[
        "predicted_price"
    ]

    model_details[
        "gru"
    ] = {
        "predicted_price":
            gru_result[
                "predicted_price"
            ],

        "weight":
            weights.get(
                "gru",
                0.0
            )
    }


    # -------------------------------------------------
    # For one-day forecast only
    # include Random Forest and XGBoost
    # -------------------------------------------------

    if horizon == 1:

        rf_result = forecast_random_forest(
            ticker=ticker
        )

        predictions[
            "random_forest"
        ] = rf_result[
            "predicted_price"
        ]

        model_details[
            "random_forest"
        ] = {
            "predicted_price":
                rf_result[
                    "predicted_price"
                ],

            "weight":
                weights.get(
                    "random_forest",
                    0.0
                )
        }


        xgb_result = forecast_xgboost(
            ticker=ticker
        )

        predictions[
            "xgboost"
        ] = xgb_result[
            "predicted_price"
        ]

        model_details[
            "xgboost"
        ] = {
            "predicted_price":
                xgb_result[
                    "predicted_price"
                ],

            "weight":
                weights.get(
                    "xgboost",
                    0.0
                )
        }


    # -------------------------------------------------
    # Calculate weighted prediction
    # -------------------------------------------------

    ensemble_price = weighted_average(
        predictions=predictions,
        weights=weights
    )


    # -------------------------------------------------
    # Current stock price
    # -------------------------------------------------

    stock = get_stock_history(
        ticker=ticker,
        limit=120
    )

    current_price = float(
        stock.iloc[-1]["close"]
    )


    # -------------------------------------------------
    # Change
    # -------------------------------------------------

    expected_change = (
        ensemble_price
        - current_price
    )

    expected_change_pct = (
        expected_change
        / current_price
        * 100
        if current_price != 0
        else 0.0
    )


    # -------------------------------------------------
    # Confidence
    # -------------------------------------------------

    volatility, confidence = (
        calculate_confidence(
            stock,
            horizon
        )
    )


    # -------------------------------------------------
    # Model agreement
    # -------------------------------------------------

    prediction_values = list(
        predictions.values()
    )

    model_spread = float(
        np.std(
            prediction_values
        )
    )

    model_spread_pct = (
        model_spread
        / current_price
        * 100
        if current_price != 0
        else 0.0
    )


    return {
        "ticker":
            ticker,

        "forecast_horizon_days":
            horizon,

        "current_price":
            round(
                current_price,
                2
            ),

        "predicted_price":
            round(
                ensemble_price,
                2
            ),

        "expected_change":
            round(
                expected_change,
                2
            ),

        "expected_change_pct":
            round(
                expected_change_pct,
                2
            ),

        "trend":
            get_trend(
                expected_change
            ),

        "volatility":
            round(
                volatility,
                6
            ),

        "confidence":
            round(
                confidence,
                4
            ),

        "confidence_pct":
            round(
                confidence * 100,
                2
            ),

        "model_spread":
            round(
                model_spread,
                4
            ),

        "model_spread_pct":
            round(
                model_spread_pct,
                2
            ),

        "models":
            model_details,

        "model":
            "Weighted Ensemble"
    }


# =================================================
# MAIN FORECAST SELECTOR
# =================================================

def forecast_stock(
    ticker: str,
    horizon: int = 7,
    model_name: str = "linear"
) -> dict:

    model_name = (
        model_name
        .strip()
        .lower()
    )


    if model_name == "linear":

        return forecast_linear(
            ticker=ticker,
            horizon=horizon
        )


    if model_name in [
        "random_forest",
        "rf"
    ]:

        return forecast_random_forest(
            ticker=ticker
        )


    if model_name in [
        "xgboost",
        "xgb"
    ]:

        return forecast_xgboost(
            ticker=ticker
        )


    if model_name == "arima":

        return forecast_arima(
            ticker=ticker,
            horizon=horizon
        )


    if model_name == "lstm":

        return forecast_lstm(
            ticker=ticker,
            horizon=horizon
        )


    if model_name == "gru":

        return forecast_gru(
            ticker=ticker,
            horizon=horizon
        )


    if model_name == "ensemble":

        return forecast_ensemble(
            ticker=ticker,
            horizon=horizon
        )


    raise ValueError(
        "Unsupported model. "
        "Use 'linear', 'random_forest', "
        "'xgboost', 'arima', 'lstm', "
        "'gru', or 'ensemble'."
    )