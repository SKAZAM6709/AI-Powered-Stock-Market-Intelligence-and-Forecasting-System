import pandas as pd

from .indicators import add_indicators


def build_features(
    df: pd.DataFrame,
    forecast_horizon: int = 1
) -> pd.DataFrame:
    """
    Create machine-learning features for stock prediction.

    Features include:
    - Returns
    - Price changes
    - Moving averages
    - EMA
    - RSI
    - MACD
    - Volatility
    - Lagged prices
    - Lagged volume

    Target:
    Future closing price after forecast_horizon days
    """

    data = df.copy()

    # Sort correctly
    data = data.sort_values(
        [
            "Name",
            "date"
        ]
    ).reset_index(
        drop=True
    )

    # -----------------------------------------
    # Add technical indicators
    # -----------------------------------------

    data = add_indicators(
        data
    )

    grouped = data.groupby(
        "Name",
        group_keys=False
    )

    # -----------------------------------------
    # Lagged closing-price features
    # -----------------------------------------

    data["close_lag_1"] = (
        grouped["close"]
        .shift(1)
    )

    data["close_lag_2"] = (
        grouped["close"]
        .shift(2)
    )

    data["close_lag_3"] = (
        grouped["close"]
        .shift(3)
    )

    data["close_lag_5"] = (
        grouped["close"]
        .shift(5)
    )

    data["close_lag_10"] = (
        grouped["close"]
        .shift(10)
    )

    # -----------------------------------------
    # Volume lag features
    # -----------------------------------------

    data["volume_lag_1"] = (
        grouped["volume"]
        .shift(1)
    )

    data["volume_lag_5"] = (
        grouped["volume"]
        .shift(5)
    )

    # -----------------------------------------
    # Rolling statistics
    # -----------------------------------------

    data["rolling_mean_5"] = (
        grouped["close"]
        .transform(
            lambda x:
                x.rolling(5).mean()
        )
    )

    data["rolling_std_5"] = (
        grouped["close"]
        .transform(
            lambda x:
                x.rolling(5).std()
        )
    )

    data["rolling_mean_10"] = (
        grouped["close"]
        .transform(
            lambda x:
                x.rolling(10).mean()
        )
    )

    data["rolling_std_10"] = (
        grouped["close"]
        .transform(
            lambda x:
                x.rolling(10).std()
        )
    )

    # -----------------------------------------
    # Price ratios
    # -----------------------------------------

    data["high_low_ratio"] = (
        data["high"]
        / data["low"]
    )

    data["open_close_ratio"] = (
        data["open"]
        / data["close"]
    )

    # -----------------------------------------
    # Intraday price range
    # -----------------------------------------

    data["price_range"] = (
        data["high"]
        - data["low"]
    )

    # -----------------------------------------
    # Percentage price range
    # -----------------------------------------

    data["price_range_pct"] = (
        (
            data["high"]
            - data["low"]
        )
        / data["close"]
        * 100
    )

    # -----------------------------------------
    # Volume change
    # -----------------------------------------

    data["volume_change"] = (
        grouped["volume"]
        .pct_change()
    )

    # -----------------------------------------
    # Momentum
    # -----------------------------------------

    data["momentum_5"] = (
        data["close"]
        - grouped["close"]
        .shift(5)
    )

    data["momentum_10"] = (
        data["close"]
        - grouped["close"]
        .shift(10)
    )

    # -----------------------------------------
    # Future price target
    # -----------------------------------------

    data["target_close"] = (
        grouped["close"]
        .shift(
            -forecast_horizon
        )
    )

    # -----------------------------------------
    # Future percentage change
    # -----------------------------------------

    data["target_return"] = (
        (
            data["target_close"]
            - data["close"]
        )
        / data["close"]
    )

    return data