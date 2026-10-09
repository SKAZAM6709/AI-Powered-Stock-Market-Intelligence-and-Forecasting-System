from pathlib import Path
import sys

PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )

import pandas as pd

from backend.app.config import settings
from backend.app.ml.preprocessing.clean_data import (
    clean_stock_dataframe
)
from backend.app.ml.forecasting.arima_model import (
    forecast_with_arima
)


def main():

    print(
        "=" * 60
    )

    print(
        "ARIMA Stock Forecast Test"
    )

    print(
        "=" * 60
    )

    print(
        "\nLoading dataset..."
    )

    df = pd.read_csv(
        settings.stock_file
    )

    df = clean_stock_dataframe(
        df
    )

    ticker = "AAPL"

    print(
        f"\nSelected ticker: {ticker}"
    )

    stock = df[
        df["Name"] == ticker
    ].copy()

    stock = stock.sort_values(
        "date"
    )

    if stock.empty:
        raise ValueError(
            f"Ticker not found: {ticker}"
        )

    prices = stock[
        "close"
    ].tail(
        250
    )

    print(
        f"Historical rows used: {len(prices)}"
    )

    print(
        "\nTraining ARIMA model..."
    )

    forecast = forecast_with_arima(
        prices=prices,
        horizon=7
    )

    print(
        "\n7-Day ARIMA Forecast:"
    )

    for day, value in enumerate(
        forecast,
        start=1
    ):

        print(
            f"Day {day}: "
            f"{float(value):.2f}"
        )

    print(
        "\nARIMA completed successfully."
    )


if __name__ == "__main__":
    main()