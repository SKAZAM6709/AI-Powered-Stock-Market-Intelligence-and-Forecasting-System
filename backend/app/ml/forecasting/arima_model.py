from statsmodels.tsa.arima.model import ARIMA


def forecast_with_arima(
    prices,
    horizon: int = 7
):
    """
    Forecast future stock prices using ARIMA.

    prices:
        Historical closing-price series.

    horizon:
        Number of future steps to predict.
    """

    if len(prices) < 30:
        raise ValueError(
            "Not enough historical data for ARIMA."
        )

    model = ARIMA(
        prices,
        order=(5, 1, 0)
    )

    fitted_model = model.fit()

    forecast = fitted_model.forecast(
        steps=horizon
    )

    return forecast