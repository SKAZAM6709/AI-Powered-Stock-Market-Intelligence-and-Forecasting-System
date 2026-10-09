from pathlib import Path
import argparse
import json
import sys

# -------------------------------------------------
# Project root
# -------------------------------------------------

PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


# -------------------------------------------------
# Imports
# -------------------------------------------------

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from sklearn.preprocessing import (
    MinMaxScaler,
)

from backend.app.config import settings

from backend.app.ml.preprocessing.clean_data import (
    clean_stock_dataframe,
)

from backend.app.ml.forecasting.lstm_model import (
    create_sequences,
    create_lstm_model,
    train_lstm_model,
)


# -------------------------------------------------
# Configuration
# -------------------------------------------------

SEQUENCE_LENGTH = 60


MODEL_ROOT = (
    PROJECT_ROOT
    / "models"
    / "time_series"
    / "lstm"
)

MODEL_ROOT.mkdir(
    parents=True,
    exist_ok=True
)


# -------------------------------------------------
# Train one ticker
# -------------------------------------------------

def train_for_ticker(
    ticker: str,
    epochs: int = 30
):

    ticker = (
        ticker
        .strip()
        .upper()
    )

    print(
        "=" * 60
    )

    print(
        "LSTM Stock Forecast Training"
    )

    print(
        "=" * 60
    )

    print(
        f"\nTicker: {ticker}"
    )

    print(
        f"Sequence length: {SEQUENCE_LENGTH}"
    )

    # -------------------------------------------------
    # Load dataset
    # -------------------------------------------------

    print(
        "\nLoading dataset..."
    )

    if not settings.stock_file.exists():

        raise FileNotFoundError(
            f"Dataset not found: "
            f"{settings.stock_file}"
        )

    df = pd.read_csv(
        settings.stock_file
    )

    print(
        f"Raw rows: {len(df)}"
    )

    # -------------------------------------------------
    # Clean dataset
    # -------------------------------------------------

    print(
        "\nCleaning dataset..."
    )

    df = clean_stock_dataframe(
        df
    )

    # -------------------------------------------------
    # Select ticker
    # -------------------------------------------------

    stock = df[
        df["Name"] == ticker
    ].copy()

    if stock.empty:

        raise ValueError(
            f"Ticker not found: {ticker}"
        )

    stock = (
        stock
        .sort_values("date")
        .reset_index(drop=True)
    )

    print(
        f"Historical rows for {ticker}: "
        f"{len(stock)}"
    )

    if len(stock) < 200:

        raise ValueError(
            f"Not enough historical data "
            f"for {ticker}. "
            f"At least 200 rows are recommended."
        )

    # -------------------------------------------------
    # Closing prices
    # -------------------------------------------------

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

    # -------------------------------------------------
    # Chronological train/test split
    # -------------------------------------------------

    split_index = int(
        len(prices)
        * 0.80
    )

    train_prices = prices[
        :split_index
    ]

    test_prices = prices[
        split_index:
    ]

    print(
        f"Training prices: "
        f"{len(train_prices)}"
    )

    print(
        f"Testing prices : "
        f"{len(test_prices)}"
    )

    # -------------------------------------------------
    # Scale prices
    # IMPORTANT:
    # Fit scaler only on training data.
    # -------------------------------------------------

    scaler = MinMaxScaler(
        feature_range=(0, 1)
    )

    scaler.fit(
        train_prices
    )

    scaled_train = scaler.transform(
        train_prices
    )

    # -------------------------------------------------
    # Create training sequences
    # -------------------------------------------------

    X_train, y_train = (
        create_sequences(
            scaled_train,
            sequence_length=SEQUENCE_LENGTH
        )
    )

    print(
        f"\nTraining sequences: "
        f"{len(X_train)}"
    )

    # -------------------------------------------------
    # Prepare testing data
    # -------------------------------------------------

    # Include previous 60 prices so the
    # first test item has enough history.

    test_context = prices[
        split_index
        - SEQUENCE_LENGTH:
    ]

    scaled_test_context = (
        scaler.transform(
            test_context
        )
    )

    X_test, y_test_scaled = (
        create_sequences(
            scaled_test_context,
            sequence_length=SEQUENCE_LENGTH
        )
    )

    y_test = (
        scaler.inverse_transform(
            y_test_scaled.reshape(
                -1,
                1
            )
        )
        .flatten()
    )

    print(
        f"Testing sequences: "
        f"{len(X_test)}"
    )

    # -------------------------------------------------
    # Create LSTM model
    # -------------------------------------------------

    print(
        "\nCreating LSTM model..."
    )

    model = create_lstm_model(
        sequence_length=SEQUENCE_LENGTH
    )

    model.summary()

    # -------------------------------------------------
    # Train
    # -------------------------------------------------

    print(
        "\nTraining LSTM..."
    )

    train_lstm_model(
        model=model,
        X_train=X_train,
        y_train=y_train,
        X_validation=X_test,
        y_validation=y_test_scaled,
        epochs=epochs,
        batch_size=32,
    )

    # -------------------------------------------------
    # Predictions
    # -------------------------------------------------

    print(
        "\nEvaluating LSTM..."
    )

    predictions_scaled = (
        model.predict(
            X_test,
            verbose=0
        )
    )

    predictions = (
        scaler.inverse_transform(
            predictions_scaled
        )
        .flatten()
    )

    # -------------------------------------------------
    # Metrics
    # -------------------------------------------------

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = (
        mean_squared_error(
            y_test,
            predictions
        )
        ** 0.5
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    # -------------------------------------------------
    # Directional accuracy
    # -------------------------------------------------

    actual_previous = prices[
        split_index - 1:
        len(prices) - 1
    ].flatten()

    actual_direction = (
        y_test
        > actual_previous
    )

    predicted_direction = (
        predictions
        > actual_previous
    )

    directional_accuracy = (
        np.mean(
            actual_direction
            == predicted_direction
        )
        * 100
    )

    # -------------------------------------------------
    # Print results
    # -------------------------------------------------

    print(
        "\n" + "=" * 60
    )

    print(
        "LSTM Evaluation Results"
    )

    print(
        "=" * 60
    )

    print(
        f"Ticker               : {ticker}"
    )

    print(
        f"MAE                  : {mae:.4f}"
    )

    print(
        f"RMSE                 : {rmse:.4f}"
    )

    print(
        f"R²                   : {r2:.4f}"
    )

    print(
        f"Directional Accuracy : "
        f"{directional_accuracy:.2f}%"
    )

    # -------------------------------------------------
    # Save model
    # -------------------------------------------------

    ticker_directory = (
        MODEL_ROOT
        / ticker
    )

    ticker_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    model_path = (
        ticker_directory
        / "lstm_model.keras"
    )

    scaler_path = (
        ticker_directory
        / "scaler.joblib"
    )

    metadata_path = (
        ticker_directory
        / "metadata.json"
    )

    model.save(
        model_path
    )

    joblib.dump(
        scaler,
        scaler_path
    )

    # -------------------------------------------------
    # Save metadata
    # -------------------------------------------------

    metadata = {
        "ticker":
            ticker,

        "sequence_length":
            SEQUENCE_LENGTH,

        "training_rows":
            int(
                len(train_prices)
            ),

        "testing_rows":
            int(
                len(test_prices)
            ),

        "mae":
            float(
                mae
            ),

        "rmse":
            float(
                rmse
            ),

        "r2":
            float(
                r2
            ),

        "directional_accuracy":
            float(
                directional_accuracy
            ),

        "model_type":
            "LSTM",

        "target":
            "next_day_close",
    }

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4
        )

    # -------------------------------------------------
    # Final output
    # -------------------------------------------------

    print(
        "\n" + "=" * 60
    )

    print(
        "LSTM training completed successfully"
    )

    print(
        "=" * 60
    )

    print(
        f"\nModel saved:\n"
        f"{model_path}"
    )

    print(
        f"\nScaler saved:\n"
        f"{scaler_path}"
    )

    print(
        f"\nMetadata saved:\n"
        f"{metadata_path}"
    )


# -------------------------------------------------
# Command line
# -------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Train an LSTM stock "
            "forecasting model."
        )
    )

    parser.add_argument(
        "--ticker",
        type=str,
        default="AAPL",
        help=(
            "Ticker to train. "
            "Default: AAPL"
        )
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=30,
        help=(
            "Maximum training epochs. "
            "Default: 30"
        )
    )

    args = parser.parse_args()

    train_for_ticker(
        ticker=args.ticker,
        epochs=args.epochs
    )


if __name__ == "__main__":
    main()