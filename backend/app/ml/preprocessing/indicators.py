import numpy as np


def add_indicators(df):
    data = df.copy()

    data = data.sort_values(
        [
            "Name",
            "date"
        ]
    )

    grouped = data.groupby(
        "Name",
        group_keys=False
    )

    # Daily percentage return
    data["daily_return"] = (
        grouped["close"]
        .pct_change()
    )

    # Daily price difference
    data["price_change"] = (
        grouped["close"]
        .diff()
    )

    # Moving averages
    data["ma_7"] = (
        grouped["close"]
        .transform(
            lambda x: x.rolling(7).mean()
        )
    )

    data["ma_20"] = (
        grouped["close"]
        .transform(
            lambda x: x.rolling(20).mean()
        )
    )

    data["ma_50"] = (
        grouped["close"]
        .transform(
            lambda x: x.rolling(50).mean()
        )
    )

    # Exponential moving averages
    data["ema_12"] = (
        grouped["close"]
        .transform(
            lambda x: x.ewm(
                span=12,
                adjust=False
            ).mean()
        )
    )

    data["ema_26"] = (
        grouped["close"]
        .transform(
            lambda x: x.ewm(
                span=26,
                adjust=False
            ).mean()
        )
    )

    # MACD
    data["macd"] = (
        data["ema_12"]
        - data["ema_26"]
    )

    data["macd_signal"] = (
        data.groupby("Name")["macd"]
        .transform(
            lambda x: x.ewm(
                span=9,
                adjust=False
            ).mean()
        )
    )

    # Volatility
    data["volatility_20"] = (
        data.groupby("Name")["daily_return"]
        .transform(
            lambda x: x.rolling(20).std()
        )
    )

    # RSI
    delta = grouped["close"].diff()

    gain = delta.clip(
        lower=0
    )

    loss = -delta.clip(
        upper=0
    )

    average_gain = (
        gain.groupby(data["Name"])
        .transform(
            lambda x: x.rolling(14).mean()
        )
    )

    average_loss = (
        loss.groupby(data["Name"])
        .transform(
            lambda x: x.rolling(14).mean()
        )
    )

    rs = (
        average_gain
        / average_loss.replace(
            0,
            np.nan
        )
    )

    data["rsi_14"] = (
        100
        - (
            100
            / (1 + rs)
        )
    )

    data["rsi_14"] = (
        data["rsi_14"]
        .fillna(50)
    )

    return data