from pathlib import Path
import sys

# -------------------------------------------------
# Add project root to Python path
# -------------------------------------------------

PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


# -------------------------------------------------
# Imports
# -------------------------------------------------

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from backend.app.config import settings

from backend.app.ml.preprocessing.clean_data import (
    clean_stock_dataframe
)

from backend.app.ml.preprocessing.feature_engineering import (
    build_features
)

from backend.app.ml.forecasting.xgboost_model import (
    create_xgboost_model
)


# -------------------------------------------------
# Model directory
# -------------------------------------------------

MODEL_DIR = (
    PROJECT_ROOT
    / "models"
    / "machine_learning"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# -------------------------------------------------
# Features
# -------------------------------------------------

FEATURE_COLUMNS = [
    "open",
    "high",
    "low",
    "close",
    "volume",

    "daily_return",
    "price_change",

    "ma_7",
    "ma_20",
    "ma_50",

    "ema_12",
    "ema_26",

    "rsi_14",
    "macd",
    "macd_signal",

    "volatility_20",

    "close_lag_1",
    "close_lag_2",
    "close_lag_3",
    "close_lag_5",
    "close_lag_10",

    "volume_lag_1",
    "volume_lag_5",

    "rolling_mean_5",
    "rolling_std_5",

    "rolling_mean_10",
    "rolling_std_10",

    "high_low_ratio",
    "open_close_ratio",

    "price_range",
    "price_range_pct",

    "volume_change",

    "momentum_5",
    "momentum_10",
]


def evaluate_model(
    model_name,
    model,
    X_train,
    y_train,
    X_test,
    y_test
):
    """
    Train and evaluate one regression model.
    """

    print(
        "\n" + "=" * 60
    )

    print(
        f"Training {model_name}"
    )

    print(
        "=" * 60
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = (
        mean_squared_error(
            y_test,
            predictions
        )
        ** 0.5
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    print(
        f"MAE  : {mae:.4f}"
    )

    print(
        f"RMSE : {rmse:.4f}"
    )

    print(
        f"R²   : {r2:.4f}"
    )

    return {
        "model": model,
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
    }


def main():

    print(
        "=" * 60
    )

    print(
        "Stock Market ML Model Training"
    )

    print(
        "=" * 60
    )

    # -------------------------------------------------
    # Load dataset
    # -------------------------------------------------

    print(
        "\nLoading dataset..."
    )

    print(
        f"Dataset path: {settings.stock_file}"
    )

    if not settings.stock_file.exists():

        raise FileNotFoundError(
            f"Dataset not found: {settings.stock_file}"
        )

    df = pd.read_csv(
        settings.stock_file
    )

    print(
        f"Raw rows: {len(df)}"
    )

    # -------------------------------------------------
    # Clean data
    # -------------------------------------------------

    print(
        "\nCleaning dataset..."
    )

    df = clean_stock_dataframe(
        df
    )

    print(
        f"Rows after cleaning: {len(df)}"
    )

    # -------------------------------------------------
    # Feature engineering
    # -------------------------------------------------

    print(
        "\nBuilding features..."
    )

    df = build_features(
        df,
        forecast_horizon=1
    )

    required_columns = (
        FEATURE_COLUMNS
        + [
            "target_close"
        ]
    )

    df = df.dropna(
        subset=required_columns
    )

    print(
        f"Training-ready rows: {len(df)}"
    )

    if len(df) < 100:

        raise ValueError(
            "Not enough data after feature engineering."
        )

    # -------------------------------------------------
    # Time ordering
    # -------------------------------------------------

    df = df.sort_values(
        "date"
    ).reset_index(
        drop=True
    )

    # -------------------------------------------------
    # Chronological train/test split
    # -------------------------------------------------

    split_index = int(
        len(df)
        * 0.80
    )

    train_df = df.iloc[
        :split_index
    ].copy()

    test_df = df.iloc[
        split_index:
    ].copy()

    X_train = train_df[
        FEATURE_COLUMNS
    ]

    y_train = train_df[
        "target_close"
    ]

    X_test = test_df[
        FEATURE_COLUMNS
    ]

    y_test = test_df[
        "target_close"
    ]

    print(
        "\nDataset split:"
    )

    print(
        f"Train size: {len(X_train)}"
    )

    print(
        f"Test size : {len(X_test)}"
    )

    # -------------------------------------------------
    # Linear Regression
    # -------------------------------------------------

    linear_model = LinearRegression()

    linear_results = evaluate_model(
        "Linear Regression",
        linear_model,
        X_train,
        y_train,
        X_test,
        y_test
    )

    # -------------------------------------------------
    # Random Forest
    # -------------------------------------------------

    random_forest_model = (
        RandomForestRegressor(
            n_estimators=150,
            max_depth=15,
            random_state=42,
            n_jobs=-1
        )
    )

    rf_results = evaluate_model(
        "Random Forest",
        random_forest_model,
        X_train,
        y_train,
        X_test,
        y_test
    )

    # -------------------------------------------------
    # XGBoost
    # -------------------------------------------------

    xgb_model = (
        create_xgboost_model()
    )

    xgb_results = evaluate_model(
        "XGBoost",
        xgb_model,
        X_train,
        y_train,
        X_test,
        y_test
    )

    # -------------------------------------------------
    # Save models
    # -------------------------------------------------

    print(
        "\nSaving trained models..."
    )

    linear_path = (
        MODEL_DIR
        / "linear_regression.joblib"
    )

    rf_path = (
        MODEL_DIR
        / "random_forest.joblib"
    )

    xgb_path = (
        MODEL_DIR
        / "xgboost.joblib"
    )

    joblib.dump(
        linear_results["model"],
        linear_path
    )

    joblib.dump(
        rf_results["model"],
        rf_path
    )

    joblib.dump(
        xgb_results["model"],
        xgb_path
    )

    # -------------------------------------------------
    # Save features
    # -------------------------------------------------

    feature_path = (
        MODEL_DIR
        / "feature_columns.joblib"
    )

    joblib.dump(
        FEATURE_COLUMNS,
        feature_path
    )

    # -------------------------------------------------
    # Save model metrics
    # -------------------------------------------------

    metrics = {

        "linear_regression": {
            "mae":
                linear_results["mae"],

            "rmse":
                linear_results["rmse"],

            "r2":
                linear_results["r2"],
        },

        "random_forest": {
            "mae":
                rf_results["mae"],

            "rmse":
                rf_results["rmse"],

            "r2":
                rf_results["r2"],
        },

        "xgboost": {
            "mae":
                xgb_results["mae"],

            "rmse":
                xgb_results["rmse"],

            "r2":
                xgb_results["r2"],
        },
    }

    metrics_path = (
        MODEL_DIR
        / "model_metrics.joblib"
    )

    joblib.dump(
        metrics,
        metrics_path
    )

    # -------------------------------------------------
    # Final results
    # -------------------------------------------------

    print(
        "\n" + "=" * 60
    )

    print(
        "Training completed successfully"
    )

    print(
        "=" * 60
    )

    print(
        "\nMODEL COMPARISON"
    )

    print(
        "-" * 60
    )

    print(
        f"Linear Regression | "
        f"MAE: {linear_results['mae']:.4f} | "
        f"RMSE: {linear_results['rmse']:.4f} | "
        f"R²: {linear_results['r2']:.4f}"
    )

    print(
        f"Random Forest     | "
        f"MAE: {rf_results['mae']:.4f} | "
        f"RMSE: {rf_results['rmse']:.4f} | "
        f"R²: {rf_results['r2']:.4f}"
    )

    print(
        f"XGBoost           | "
        f"MAE: {xgb_results['mae']:.4f} | "
        f"RMSE: {xgb_results['rmse']:.4f} | "
        f"R²: {xgb_results['r2']:.4f}"
    )

    print(
        "\nSaved models:"
    )

    print(
        linear_path
    )

    print(
        rf_path
    )

    print(
        xgb_path
    )

    print(
        feature_path
    )

    print(
        metrics_path
    )


if __name__ == "__main__":
    main()