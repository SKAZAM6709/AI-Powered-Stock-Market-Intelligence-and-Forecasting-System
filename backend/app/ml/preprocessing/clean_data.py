import pandas as pd

from ...utils.constants import REQUIRED_STOCK_COLUMNS


def clean_stock_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    missing_columns = [
        column
        for column in REQUIRED_STOCK_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    data = df.copy()

    data.columns = [
        column.strip()
        for column in data.columns
    ]

    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce"
    )

    data["Name"] = (
        data["Name"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    data = data.dropna(
        subset=[
            "date",
            "Name",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
    )

    data = data[
        (data["open"] > 0)
        & (data["high"] > 0)
        & (data["low"] > 0)
        & (data["close"] > 0)
        & (data["volume"] >= 0)
    ]

    data = data.drop_duplicates(
        subset=[
            "Name",
            "date"
        ],
        keep="last"
    )

    data = data.sort_values(
        by=[
            "Name",
            "date"
        ]
    )

    data = data.reset_index(
        drop=True
    )

    return data