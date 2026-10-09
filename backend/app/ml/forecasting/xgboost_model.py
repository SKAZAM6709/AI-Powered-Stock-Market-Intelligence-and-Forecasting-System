from xgboost import XGBRegressor


def create_xgboost_model():
    """
    Create the XGBoost regression model
    used for next-day stock-price prediction.
    """

    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        min_child_weight=2,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1,
    )

    return model