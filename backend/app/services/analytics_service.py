from pathlib import Path
import json

import joblib
import pandas as pd


PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]


# =================================================
# FORECAST MODEL METRICS
# =================================================

ML_MODEL_DIR = (
    PROJECT_ROOT
    / "models"
    / "machine_learning"
)

MODEL_METRICS_FILE = (
    ML_MODEL_DIR
    / "model_metrics.joblib"
)


# =================================================
# SENTIMENT METRICS
# =================================================

SENTIMENT_METRICS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sentiment_metrics.json"
)

SENTIMENT_COMPARISON_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sentiment_comparison.csv"
)


# =================================================
# LOAD FORECAST METRICS
# =================================================

def load_model_metrics():
    """
    Load ML forecasting metrics.
    """

    if not MODEL_METRICS_FILE.exists():

        raise FileNotFoundError(
            "Forecast model metrics file not found. "
            "Run scripts/train_ml_models.py first."
        )

    return joblib.load(
        MODEL_METRICS_FILE
    )


# =================================================
# FORECAST MODEL METRICS
# =================================================

def get_model_metrics():
    """
    Return forecasting model metrics.
    """

    metrics = load_model_metrics()

    return {
        "models": metrics
    }


# =================================================
# BEST FORECAST MODELS
# =================================================

def get_best_models():
    """
    Determine best forecasting models
    according to available metrics.
    """

    metrics = load_model_metrics()

    if not metrics:

        raise ValueError(
            "No model metrics available."
        )

    # -----------------------------------------
    # MAE - lower is better
    # -----------------------------------------

    best_mae = min(
        metrics.items(),
        key=lambda item: item[1]["mae"]
    )

    # -----------------------------------------
    # RMSE - lower is better
    # -----------------------------------------

    best_rmse = min(
        metrics.items(),
        key=lambda item: item[1]["rmse"]
    )

    # -----------------------------------------
    # R2 - higher is better
    # -----------------------------------------

    best_r2 = max(
        metrics.items(),
        key=lambda item: item[1]["r2"]
    )

    return {
        "best_mae": {
            "model": best_mae[0],
            "value": best_mae[1]["mae"],
        },

        "best_rmse": {
            "model": best_rmse[0],
            "value": best_rmse[1]["rmse"],
        },

        "best_r2": {
            "model": best_r2[0],
            "value": best_r2[1]["r2"],
        },
    }


# =================================================
# FORECAST ANALYTICS OVERVIEW
# =================================================

def get_analytics_overview():
    """
    Return forecasting analytics overview.
    """

    metrics = load_model_metrics()

    best_models = get_best_models()

    return {
        "total_models":
            len(metrics),

        "models":
            list(
                metrics.keys()
            ),

        "best_models":
            best_models,
    }


# =================================================
# LOAD SENTIMENT METRICS
# =================================================

def load_sentiment_metrics():
    """
    Load sentiment evaluation metrics.
    """

    if not SENTIMENT_METRICS_FILE.exists():

        raise FileNotFoundError(
            "Sentiment metrics file not found. "
            "Run scripts/process_finbert_sentiment.py first."
        )

    with open(
        SENTIMENT_METRICS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file
        )


# =================================================
# SENTIMENT MODEL COMPARISON
# =================================================

def get_sentiment_model_comparison():
    """
    Compare VADER and FinBERT performance.
    """

    metrics = load_sentiment_metrics()

    vader_accuracy = float(
        metrics["vader"]["accuracy"]
    )

    finbert_accuracy = float(
        metrics["finbert"]["accuracy"]
    )

    agreement = float(
        metrics[
            "vader_finbert_agreement"
        ]
    )

    if finbert_accuracy > vader_accuracy:

        best_model = "FinBERT"

    elif vader_accuracy > finbert_accuracy:

        best_model = "VADER"

    else:

        best_model = "Tie"

    return {
        "total_records":
            metrics.get(
                "total_records",
                0
            ),

        "vader_accuracy":
            round(
                vader_accuracy,
                4
            ),

        "vader_accuracy_pct":
            round(
                vader_accuracy * 100,
                2
            ),

        "finbert_accuracy":
            round(
                finbert_accuracy,
                4
            ),

        "finbert_accuracy_pct":
            round(
                finbert_accuracy * 100,
                2
            ),

        "agreement":
            round(
                agreement,
                4
            ),

        "agreement_pct":
            round(
                agreement * 100,
                2
            ),

        "best_model":
            best_model,
    }


# =================================================
# SENTIMENT CONFUSION MATRICES
# =================================================

def get_sentiment_confusion_matrices():
    """
    Return VADER and FinBERT confusion matrices.
    """

    metrics = load_sentiment_metrics()

    return {
        "labels":
            metrics[
                "labels"
            ],

        "vader":
            metrics[
                "vader"
            ][
                "confusion_matrix"
            ],

        "finbert":
            metrics[
                "finbert"
            ][
                "confusion_matrix"
            ],
    }


# =================================================
# SENTIMENT CLASSIFICATION REPORTS
# =================================================

def get_sentiment_classification_reports():
    """
    Return precision, recall, F1-score
    and support for VADER and FinBERT.
    """

    metrics = load_sentiment_metrics()

    return {
        "vader":
            metrics[
                "vader"
            ][
                "classification_report"
            ],

        "finbert":
            metrics[
                "finbert"
            ][
                "classification_report"
            ],
    }


# =================================================
# SENTIMENT PREDICTION DISTRIBUTIONS
# =================================================

def get_sentiment_distribution():
    """
    Return label distributions for:

    - original labels
    - VADER
    - FinBERT
    """

    if not SENTIMENT_COMPARISON_FILE.exists():

        raise FileNotFoundError(
            "Sentiment comparison file not found. "
            "Run scripts/process_finbert_sentiment.py first."
        )

    df = pd.read_csv(
        SENTIMENT_COMPARISON_FILE
    )

    required_columns = [
        "original_sentiment",
        "vader_sentiment",
        "finbert_sentiment",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing sentiment columns: {missing}"
        )

    def counts(column_name):

        values = (
            df[
                column_name
            ]
            .astype(str)
            .str.lower()
            .str.strip()
            .value_counts()
            .to_dict()
        )

        return {
            str(key):
                int(value)

            for key, value
            in values.items()
        }

    return {
        "total_records":
            len(df),

        "original":
            counts(
                "original_sentiment"
            ),

        "vader":
            counts(
                "vader_sentiment"
            ),

        "finbert":
            counts(
                "finbert_sentiment"
            ),
    }