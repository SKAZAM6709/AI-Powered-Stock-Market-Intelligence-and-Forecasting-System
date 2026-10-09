from functools import lru_cache

import pandas as pd

from ..config import settings
from ..ml.preprocessing.clean_data import clean_stock_dataframe
from ..ml.preprocessing.indicators import add_indicators


@lru_cache(maxsize=1)
def load_stock_data() -> pd.DataFrame:
    """
    Load and clean the stock dataset.

    The result is cached so the CSV is not reloaded
    on every API request.
    """

    file_path = settings.stock_file

    if not file_path.exists():
        raise FileNotFoundError(
            f"Stock dataset not found: {file_path}"
        )

    df = pd.read_csv(
        file_path
    )

    cleaned_df = clean_stock_dataframe(
        df
    )

    return cleaned_df


def get_tickers() -> list[str]:
    """
    Return all available stock ticker symbols.
    """

    df = load_stock_data()

    tickers = (
        df["Name"]
        .dropna()
        .astype(str)
        .str.upper()
        .unique()
        .tolist()
    )

    return sorted(
        tickers
    )


def get_stock_history(
    ticker: str,
    limit: int = 365
) -> pd.DataFrame:
    """
    Return historical stock data
    for one ticker.
    """

    ticker = ticker.strip().upper()

    df = load_stock_data()

    stock = df[
        df["Name"] == ticker
    ].copy()

    if stock.empty:
        raise ValueError(
            f"Ticker not found: {ticker}"
        )

    stock = stock.sort_values(
        "date"
    )

    return stock.tail(
        limit
    ).reset_index(
        drop=True
    )


def get_stock_summary(
    ticker: str
) -> dict:
    """
    Return the latest OHLCV values
    and daily price change.
    """

    stock = get_stock_history(
        ticker,
        limit=2
    )

    latest = stock.iloc[-1]

    if len(stock) > 1:
        previous_close = float(
            stock.iloc[-2]["close"]
        )
    else:
        previous_close = float(
            latest["close"]
        )

    current_close = float(
        latest["close"]
    )

    daily_change = (
        current_close
        - previous_close
    )

    daily_change_pct = (
        daily_change
        / previous_close
        * 100
        if previous_close != 0
        else 0.0
    )

    return {
        "ticker": ticker.strip().upper(),
        "latest_date": latest["date"].strftime(
            "%Y-%m-%d"
        ),
        "open": float(
            latest["open"]
        ),
        "high": float(
            latest["high"]
        ),
        "low": float(
            latest["low"]
        ),
        "close": current_close,
        "volume": float(
            latest["volume"]
        ),
        "daily_change": float(
            daily_change
        ),
        "daily_change_pct": float(
            daily_change_pct
        ),
    }


def get_stock_indicators(
    ticker: str,
    limit: int = 365
) -> pd.DataFrame:
    """
    Return technical indicators for a stock.

    Indicators:
    - Daily return
    - Price change
    - MA 7
    - MA 20
    - MA 50
    - EMA 12
    - EMA 26
    - MACD
    - MACD signal
    - RSI 14
    - 20-day volatility
    """

    # We load at least 80 rows so indicators
    # such as MA50 have enough historical data.
    stock = get_stock_history(
        ticker,
        limit=max(
            limit,
            80
        )
    )

    stock_with_indicators = add_indicators(
        stock
    )

    return (
        stock_with_indicators
        .tail(limit)
        .reset_index(
            drop=True
        )
    )