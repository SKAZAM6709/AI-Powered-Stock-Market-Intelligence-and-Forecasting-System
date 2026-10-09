from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from ..services.forecast_service import (
    forecast_stock,
)


router = APIRouter(
    prefix="/forecast",
    tags=["Forecast"],
)


@router.get("/{ticker}")
def forecast(
    ticker: str,

    horizon: int = Query(
        7,
        ge=1,
        le=60,
        description=(
            "Number of future trading days "
            "to forecast."
        )
    ),

    model: str = Query(
        "linear",
        description=(
            "Available models: "
            "linear, random_forest, "
            "xgboost, arima, lstm, "
            "gru, or ensemble."
        )
    )
):
    """
    Generate stock-price forecasts.

    Available models:

    - linear
    - random_forest
    - xgboost
    - arima
    - lstm
    - gru
    - ensemble

    Notes:

    Random Forest and XGBoost currently
    perform one-day-ahead forecasting.

    Linear Regression and ARIMA support
    multi-day forecasting.

    LSTM and GRU use recursive multi-day
    forecasting.

    Ensemble combines available models
    using weighted averaging.
    """

    try:

        result = forecast_stock(
            ticker=ticker,
            horizon=horizon,
            model_name=model
        )

        return result


    except FileNotFoundError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Forecast generation failed: "
                f"{str(error)}"
            )
        )