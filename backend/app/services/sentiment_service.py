from pathlib import Path

import pandas as pd

from ..ml.sentiment.sentiment_pipeline import (
    analyze_sentiment,
)


# =================================================
# PROJECT PATH
# =================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]


SENTIMENT_DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sentiment_data.csv"
)


# =================================================
# SINGLE TEXT ANALYSIS
# =================================================

def get_text_sentiment(
    text: str,
    model_name: str = "vader"
) -> dict:

    return analyze_sentiment(
        text=text,
        model_name=model_name
    )


# =================================================
# LOAD SENTIMENT DATA
# =================================================

def load_sentiment_data() -> pd.DataFrame:

    if not SENTIMENT_DATA_FILE.exists():

        raise FileNotFoundError(
            f"Sentiment dataset not found: "
            f"{SENTIMENT_DATA_FILE}"
        )

    df = pd.read_csv(
        SENTIMENT_DATA_FILE
    )

    if df.empty:

        raise ValueError(
            "Sentiment dataset is empty."
        )

    return df


# =================================================
# COLUMN DETECTION
# =================================================

def find_column(
    df: pd.DataFrame,
    candidates: list[str]
):

    column_map = {
        str(column)
        .lower()
        .strip():
            column

        for column
        in df.columns
    }

    for candidate in candidates:

        candidate = (
            candidate
            .lower()
            .strip()
        )

        if candidate in column_map:

            return column_map[
                candidate
            ]

    return None


def get_ticker_column(
    df: pd.DataFrame
):

    return find_column(
        df,
        [
            "ticker",
            "symbol",
            "stock",
            "name",
            "company_symbol",
        ]
    )


def get_text_column(
    df: pd.DataFrame
):

    return find_column(
        df,
        [
            "headline",
            "title",
            "news",
            "text",
            "description",
            "summary",
            "article",
            "content",
        ]
    )


def get_sentiment_column(
    df: pd.DataFrame
):

    return find_column(
        df,
        [
            "sentiment",
            "sentiment_label",
            "label",
            "sentiment_class",
        ]
    )


def get_score_column(
    df: pd.DataFrame
):

    return find_column(
        df,
        [
            "sentiment_score",
            "compound",
            "compound_score",
            "score",
            "polarity",
        ]
    )


# =================================================
# DATASET INFORMATION
# =================================================

def get_sentiment_dataset_info() -> dict:

    df = load_sentiment_data()

    return {
        "rows":
            len(df),

        "columns":
            list(
                df.columns
            ),

        "ticker_column":
            get_ticker_column(
                df
            ),

        "text_column":
            get_text_column(
                df
            ),

        "sentiment_column":
            get_sentiment_column(
                df
            ),

        "score_column":
            get_score_column(
                df
            ),

        "file":
            str(
                SENTIMENT_DATA_FILE
            ),
    }


# =================================================
# NEWS RECORDS
# =================================================

def get_news_records(
    limit: int = 50
) -> dict:

    df = load_sentiment_data()

    limit = max(
        1,
        min(
            int(limit),
            500
        )
    )

    records = (
        df
        .head(limit)
        .fillna("")
        .to_dict(
            orient="records"
        )
    )

    return {
        "count":
            len(records),

        "total":
            len(df),

        "data":
            records,
    }


# =================================================
# OVERALL SUMMARY
# =================================================

def get_sentiment_summary() -> dict:

    df = load_sentiment_data()

    sentiment_column = (
        get_sentiment_column(
            df
        )
    )

    score_column = (
        get_score_column(
            df
        )
    )

    result = {
        "total_records":
            len(df),
    }

    # -----------------------------------------
    # Sentiment counts
    # -----------------------------------------

    if sentiment_column:

        counts = (
            df[
                sentiment_column
            ]
            .astype(str)
            .str.strip()
            .value_counts()
            .to_dict()
        )

        result[
            "sentiment_counts"
        ] = {
            str(key):
                int(value)

            for key, value
            in counts.items()
        }

    else:

        result[
            "sentiment_counts"
        ] = {}

    # -----------------------------------------
    # Score statistics
    # -----------------------------------------

    if score_column:

        numeric_scores = (
            pd.to_numeric(
                df[
                    score_column
                ],
                errors="coerce"
            )
            .dropna()
        )

        if len(numeric_scores) > 0:

            result[
                "average_sentiment_score"
            ] = round(
                float(
                    numeric_scores.mean()
                ),
                4
            )

            result[
                "minimum_sentiment_score"
            ] = round(
                float(
                    numeric_scores.min()
                ),
                4
            )

            result[
                "maximum_sentiment_score"
            ] = round(
                float(
                    numeric_scores.max()
                ),
                4
            )

        else:

            result[
                "average_sentiment_score"
            ] = None

    else:

        result[
            "average_sentiment_score"
        ] = None

    return result


# =================================================
# TICKER SENTIMENT
# =================================================

def get_ticker_sentiment(
    ticker: str,
    limit: int = 50
) -> dict:

    ticker = (
        ticker
        .strip()
        .upper()
    )

    df = load_sentiment_data()

    ticker_column = (
        get_ticker_column(
            df
        )
    )

    if ticker_column is None:

        raise ValueError(
            "No ticker/symbol column was found "
            "in sentiment_data.csv."
        )

    ticker_data = df[
        df[
            ticker_column
        ]
        .astype(str)
        .str.upper()
        .str.strip()
        == ticker
    ].copy()

    if ticker_data.empty:

        raise ValueError(
            f"No sentiment records found "
            f"for ticker {ticker}."
        )

    sentiment_column = (
        get_sentiment_column(
            ticker_data
        )
    )

    score_column = (
        get_score_column(
            ticker_data
        )
    )

    result = {
        "ticker":
            ticker,

        "total_records":
            len(
                ticker_data
            ),
    }

    if sentiment_column:

        counts = (
            ticker_data[
                sentiment_column
            ]
            .astype(str)
            .str.strip()
            .value_counts()
            .to_dict()
        )

        result[
            "sentiment_counts"
        ] = {
            str(key):
                int(value)

            for key, value
            in counts.items()
        }

    else:

        result[
            "sentiment_counts"
        ] = {}

    if score_column:

        scores = pd.to_numeric(
            ticker_data[
                score_column
            ],
            errors="coerce"
        ).dropna()

        if len(scores) > 0:

            result[
                "average_sentiment_score"
            ] = round(
                float(
                    scores.mean()
                ),
                4
            )

        else:

            result[
                "average_sentiment_score"
            ] = None

    else:

        result[
            "average_sentiment_score"
        ] = None

    limit = max(
        1,
        min(
            int(limit),
            200
        )
    )

    result[
        "news"
    ] = (
        ticker_data
        .head(limit)
        .fillna("")
        .to_dict(
            orient="records"
        )
    )

    return result