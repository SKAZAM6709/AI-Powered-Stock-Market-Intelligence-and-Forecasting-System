from pathlib import Path
import json
import sys

PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


import numpy as np
import pandas as pd
import torch

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

from backend.app.ml.sentiment.finbert_model import (
    load_finbert,
)


# =================================================
# FILE PATHS
# =================================================

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sentiment_data.csv"
)


OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sentiment_comparison.csv"
)


METRICS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sentiment_metrics.json"
)


# =================================================
# SETTINGS
# =================================================

BATCH_SIZE = 16

LABELS = [
    "negative",
    "neutral",
    "positive",
]


# =================================================
# FINBERT BATCH PREDICTION
# =================================================

def predict_finbert_batch(
    texts,
    tokenizer,
    model
):
    """
    Run FinBERT prediction for
    a batch of financial headlines.
    """

    inputs = tokenizer(
        texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512,
    )

    with torch.no_grad():

        outputs = model(
            **inputs
        )

    probabilities = (
        torch.nn.functional.softmax(
            outputs.logits,
            dim=-1
        )
        .cpu()
        .numpy()
    )

    id2label = model.config.id2label

    results = []

    for probability_values in probabilities:

        score_map = {}

        for index, probability in enumerate(
            probability_values
        ):

            label = str(
                id2label[index]
            ).lower()

            score_map[label] = float(
                probability
            )

        positive = score_map.get(
            "positive",
            0.0
        )

        negative = score_map.get(
            "negative",
            0.0
        )

        neutral = score_map.get(
            "neutral",
            0.0
        )

        label_scores = {
            "positive":
                positive,

            "negative":
                negative,

            "neutral":
                neutral,
        }

        predicted_label = max(
            label_scores,
            key=label_scores.get
        )

        confidence = max(
            label_scores.values()
        )

        compound = (
            positive
            - negative
        )

        results.append(
            {
                "sentiment":
                    predicted_label,

                "confidence":
                    confidence,

                "positive":
                    positive,

                "neutral":
                    neutral,

                "negative":
                    negative,

                "compound":
                    compound,
            }
        )

    return results


# =================================================
# MAIN PROCESSING
# =================================================

def process_finbert():

    print(
        "=" * 70
    )

    print(
        "FinBERT Financial News Sentiment Evaluation"
    )

    print(
        "=" * 70
    )

    # -----------------------------------------
    # Check dataset
    # -----------------------------------------

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input dataset not found: "
            f"{INPUT_FILE}"
        )

    # -----------------------------------------
    # Load dataset
    # -----------------------------------------

    print(
        "\nLoading processed sentiment dataset..."
    )

    df = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"Rows loaded: {len(df)}"
    )

    print(
        f"Columns: {list(df.columns)}"
    )

    required_columns = [
        "original_sentiment",
        "headline",
        "sentiment",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing required columns: "
            f"{missing_columns}"
        )

    # -----------------------------------------
    # Clean labels
    # -----------------------------------------

    df[
        "original_sentiment"
    ] = (
        df[
            "original_sentiment"
        ]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    df[
        "vader_sentiment"
    ] = (
        df[
            "sentiment"
        ]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    # Rename existing VADER columns
    df = df.rename(
        columns={
            "sentiment_score":
                "vader_compound",

            "positive_score":
                "vader_positive",

            "neutral_score":
                "vader_neutral",

            "negative_score":
                "vader_negative",
        }
    )

    # -----------------------------------------
    # Load FinBERT once
    # -----------------------------------------

    print(
        "\nLoading FinBERT..."
    )

    tokenizer, model = (
        load_finbert()
    )

    print(
        "FinBERT loaded successfully."
    )

    # -----------------------------------------
    # Storage
    # -----------------------------------------

    finbert_labels = []

    finbert_confidence = []

    finbert_positive = []

    finbert_neutral = []

    finbert_negative = []

    finbert_compound = []

    total_rows = len(df)

    # -----------------------------------------
    # Batch processing
    # -----------------------------------------

    print(
        "\nRunning FinBERT on all headlines..."
    )

    for start in range(
        0,
        total_rows,
        BATCH_SIZE
    ):

        end = min(
            start + BATCH_SIZE,
            total_rows
        )

        batch_texts = (
            df[
                "headline"
            ]
            .iloc[start:end]
            .astype(str)
            .tolist()
        )

        batch_results = (
            predict_finbert_batch(
                batch_texts,
                tokenizer,
                model
            )
        )

        for result in batch_results:

            finbert_labels.append(
                result[
                    "sentiment"
                ]
            )

            finbert_confidence.append(
                result[
                    "confidence"
                ]
            )

            finbert_positive.append(
                result[
                    "positive"
                ]
            )

            finbert_neutral.append(
                result[
                    "neutral"
                ]
            )

            finbert_negative.append(
                result[
                    "negative"
                ]
            )

            finbert_compound.append(
                result[
                    "compound"
                ]
            )

        print(
            f"Processed "
            f"{end}/{total_rows}"
        )

    # =========================================
    # ADD FINBERT COLUMNS
    # =========================================

    df[
        "finbert_sentiment"
    ] = finbert_labels

    df[
        "finbert_confidence"
    ] = finbert_confidence

    df[
        "finbert_positive"
    ] = finbert_positive

    df[
        "finbert_neutral"
    ] = finbert_neutral

    df[
        "finbert_negative"
    ] = finbert_negative

    df[
        "finbert_compound"
    ] = finbert_compound


    # =========================================
    # ORIGINAL LABELS
    # =========================================

    y_true = df[
        "original_sentiment"
    ]

    vader_predictions = df[
        "vader_sentiment"
    ]

    finbert_predictions = df[
        "finbert_sentiment"
    ]


    # =========================================
    # ACCURACY
    # =========================================

    vader_accuracy = accuracy_score(
        y_true,
        vader_predictions
    )

    finbert_accuracy = accuracy_score(
        y_true,
        finbert_predictions
    )


    # =========================================
    # AGREEMENT BETWEEN VADER AND FINBERT
    # =========================================

    vader_finbert_agreement = (
        np.mean(
            vader_predictions
            == finbert_predictions
        )
    )


    # =========================================
    # CLASSIFICATION REPORTS
    # =========================================

    vader_report = classification_report(
        y_true,
        vader_predictions,
        labels=LABELS,
        output_dict=True,
        zero_division=0
    )

    finbert_report = classification_report(
        y_true,
        finbert_predictions,
        labels=LABELS,
        output_dict=True,
        zero_division=0
    )


    # =========================================
    # CONFUSION MATRICES
    # =========================================

    vader_matrix = confusion_matrix(
        y_true,
        vader_predictions,
        labels=LABELS
    )

    finbert_matrix = confusion_matrix(
        y_true,
        finbert_predictions,
        labels=LABELS
    )


    # =========================================
    # SAVE COMPARISON DATASET
    # =========================================

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8"
    )


    # =========================================
    # SAVE METRICS
    # =========================================

    metrics = {
        "total_records":
            int(
                len(df)
            ),

        "labels":
            LABELS,

        "vader": {
            "accuracy":
                float(
                    vader_accuracy
                ),

            "classification_report":
                vader_report,

            "confusion_matrix":
                vader_matrix.tolist(),
        },

        "finbert": {
            "accuracy":
                float(
                    finbert_accuracy
                ),

            "classification_report":
                finbert_report,

            "confusion_matrix":
                finbert_matrix.tolist(),
        },

        "vader_finbert_agreement":
            float(
                vader_finbert_agreement
            ),
    }


    with open(
        METRICS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metrics,
            file,
            indent=4
        )


    # =========================================
    # PRINT RESULTS
    # =========================================

    print(
        "\n" + "=" * 70
    )

    print(
        "SENTIMENT MODEL COMPARISON"
    )

    print(
        "=" * 70
    )

    print(
        f"\nTotal headlines: "
        f"{len(df)}"
    )

    print(
        "\nVADER Accuracy:"
    )

    print(
        f"{vader_accuracy * 100:.2f}%"
    )

    print(
        "\nFinBERT Accuracy:"
    )

    print(
        f"{finbert_accuracy * 100:.2f}%"
    )

    print(
        "\nVADER / FinBERT Agreement:"
    )

    print(
        f"{vader_finbert_agreement * 100:.2f}%"
    )


    # =========================================
    # SENTIMENT DISTRIBUTION
    # =========================================

    print(
        "\n" + "=" * 70
    )

    print(
        "Original Sentiment Distribution"
    )

    print(
        "=" * 70
    )

    print(
        y_true.value_counts()
    )


    print(
        "\n" + "=" * 70
    )

    print(
        "VADER Distribution"
    )

    print(
        "=" * 70
    )

    print(
        vader_predictions.value_counts()
    )


    print(
        "\n" + "=" * 70
    )

    print(
        "FinBERT Distribution"
    )

    print(
        "=" * 70
    )

    print(
        finbert_predictions.value_counts()
    )


    # =========================================
    # CLASSIFICATION REPORT
    # =========================================

    print(
        "\n" + "=" * 70
    )

    print(
        "FinBERT Classification Report"
    )

    print(
        "=" * 70
    )

    print(
        classification_report(
            y_true,
            finbert_predictions,
            labels=LABELS,
            zero_division=0
        )
    )


    print(
        "\nComparison dataset saved to:"
    )

    print(
        OUTPUT_FILE
    )


    print(
        "\nMetrics saved to:"
    )

    print(
        METRICS_FILE
    )


if __name__ == "__main__":

    process_finbert()