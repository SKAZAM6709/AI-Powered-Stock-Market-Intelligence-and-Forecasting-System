from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )

import pandas as pd

from backend.app.ml.sentiment.sentiment_pipeline import (
    analyze_sentiment,
)


INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "financial_news.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sentiment_data.csv"
)


def process_news():

    print("=" * 60)
    print("Financial News Sentiment Processing")
    print("=" * 60)

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )

    print(
        f"\nInput file:\n{INPUT_FILE}"
    )

    # =========================================
    # LOAD DATASET
    # =========================================

    df = pd.read_csv(
        INPUT_FILE,
        encoding="latin-1",
        header=None,
        names=[
            "original_sentiment",
            "headline"
        ]
    )

    print(
        f"\nRows loaded: {len(df)}"
    )

    print(
        f"Columns: {list(df.columns)}"
    )

    # =========================================
    # CLEAN DATA
    # =========================================

    df = df.dropna(
        subset=[
            "headline"
        ]
    ).copy()

    df["headline"] = (
        df["headline"]
        .astype(str)
        .str.strip()
    )

    df = df[
        df["headline"] != ""
    ].copy()

    print(
        f"Valid rows: {len(df)}"
    )

    # =========================================
    # VADER RESULTS
    # =========================================

    vader_sentiments = []
    compound_scores = []
    positive_scores = []
    neutral_scores = []
    negative_scores = []

    print(
        "\nRunning VADER sentiment analysis..."
    )

    total = len(df)

    for number, headline in enumerate(
        df["headline"],
        start=1
    ):

        result = analyze_sentiment(
            headline
        )

        vader_sentiments.append(
            result["sentiment"]
        )

        compound_scores.append(
            result["compound"]
        )

        positive_scores.append(
            result["positive"]
        )

        neutral_scores.append(
            result["neutral"]
        )

        negative_scores.append(
            result["negative"]
        )

        if (
            number % 500 == 0
            or number == total
        ):

            print(
                f"Processed {number}/{total}"
            )

    # =========================================
    # ADD COLUMNS
    # =========================================

    df["sentiment"] = (
        vader_sentiments
    )

    df["sentiment_score"] = (
        compound_scores
    )

    df["positive_score"] = (
        positive_scores
    )

    df["neutral_score"] = (
        neutral_scores
    )

    df["negative_score"] = (
        negative_scores
    )

    df["sentiment_model"] = (
        "VADER"
    )

    # =========================================
    # SAVE
    # =========================================

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8"
    )

    # =========================================
    # SUMMARY
    # =========================================

    print(
        "\n" + "=" * 60
    )

    print(
        "Original Dataset Sentiment"
    )

    print(
        "=" * 60
    )

    print(
        df[
            "original_sentiment"
        ].value_counts()
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "VADER Sentiment"
    )

    print(
        "=" * 60
    )

    print(
        df[
            "sentiment"
        ].value_counts()
    )

    print(
        "\nAverage VADER score:"
    )

    print(
        round(
            float(
                df[
                    "sentiment_score"
                ].mean()
            ),
            4
        )
    )

    print(
        "\nProcessed dataset saved to:"
    )

    print(
        OUTPUT_FILE
    )


if __name__ == "__main__":
    process_news()