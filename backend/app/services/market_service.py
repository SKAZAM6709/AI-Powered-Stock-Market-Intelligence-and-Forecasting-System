from .stock_service import load_stock_data


def get_market_overview(limit: int = 5):
    """
    Return market overview information:
    - Top gainers
    - Top losers
    - Most active stocks
    """

    df = load_stock_data()

    df = df.sort_values(
        [
            "Name",
            "date"
        ]
    )

    # Take the last two records for each stock
    latest_two = (
        df.groupby("Name")
        .tail(2)
        .copy()
    )

    # Previous close for each stock
    latest_two["previous_close"] = (
        latest_two
        .groupby("Name")["close"]
        .shift(1)
    )

    # Percentage change
    latest_two["change_pct"] = (
        (
            latest_two["close"]
            - latest_two["previous_close"]
        )
        / latest_two["previous_close"]
        * 100
    )

    # Keep only latest record for each stock
    latest = (
        latest_two
        .groupby("Name")
        .tail(1)
        .copy()
    )

    # Remove rows without previous close
    latest = latest.dropna(
        subset=["change_pct"]
    )

    def format_rows(frame):
        result = []

        for _, row in frame.iterrows():
            result.append(
                {
                    "ticker": row["Name"],
                    "close": float(
                        row["close"]
                    ),
                    "change_pct": float(
                        row["change_pct"]
                    ),
                    "volume": float(
                        row["volume"]
                    ),
                }
            )

        return result

    # Top gainers
    top_gainers = latest.nlargest(
        limit,
        "change_pct"
    )

    # Top losers
    top_losers = latest.nsmallest(
        limit,
        "change_pct"
    )

    # Most active stocks
    most_active = latest.nlargest(
        limit,
        "volume"
    )

    return {
        "top_gainers": format_rows(
            top_gainers
        ),
        "top_losers": format_rows(
            top_losers
        ),
        "most_active": format_rows(
            most_active
        ),
    }