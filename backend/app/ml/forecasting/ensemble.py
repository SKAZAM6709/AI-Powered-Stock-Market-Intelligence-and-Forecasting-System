def weighted_average(
    predictions: dict,
    weights: dict
) -> float:
    """
    Calculate weighted average forecast.

    predictions example:
    {
        "linear": 160.5,
        "arima": 161.2,
        "lstm": 159.8,
        "gru": 158.9
    }

    weights example:
    {
        "linear": 0.20,
        "arima": 0.30,
        "lstm": 0.30,
        "gru": 0.20
    }
    """

    total_weight = 0.0
    weighted_sum = 0.0

    for model_name, prediction in predictions.items():

        if model_name not in weights:
            continue

        weight = weights[
            model_name
        ]

        weighted_sum += (
            prediction
            * weight
        )

        total_weight += weight

    if total_weight == 0:

        raise ValueError(
            "No valid ensemble weights were provided."
        )

    final_prediction = (
        weighted_sum
        / total_weight
    )

    return float(
        final_prediction
    )


def get_ensemble_weights(
    horizon: int
) -> dict:
    """
    Return model weights.

    For 1-day forecasts:
    use all six models.

    For multi-day forecasts:
    use models that support
    multi-day prediction.
    """

    if horizon == 1:

        return {
            "linear": 0.15,
            "random_forest": 0.20,
            "xgboost": 0.10,
            "arima": 0.20,
            "lstm": 0.20,
            "gru": 0.15,
        }

    return {
        "linear": 0.20,
        "arima": 0.30,
        "lstm": 0.30,
        "gru": 0.20,
    }