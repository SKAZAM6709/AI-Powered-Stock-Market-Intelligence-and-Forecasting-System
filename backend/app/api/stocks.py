import numpy as np

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from ..services.stock_service import (
    get_tickers,
    get_stock_history,
    get_stock_summary,
    get_stock_indicators,
)


router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"],
)


@router.get("")
def list_stocks():

    return {
        "tickers": get_tickers()
    }


@router.get("/{ticker}")
def stock_summary(
    ticker: str
):

    try:

        return get_stock_summary(
            ticker
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


@router.get("/{ticker}/history")
def stock_history(
    ticker: str,
    limit: int = Query(
        365,
        ge=10,
        le=5000
    )
):

    try:

        df = get_stock_history(
            ticker,
            limit
        )

        result = df.copy()

        result["date"] = (
            result["date"]
            .dt.strftime(
                "%Y-%m-%d"
            )
        )

        return result[
            [
                "date",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ]
        ].to_dict(
            orient="records"
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


@router.get("/{ticker}/indicators")
def stock_indicators(
    ticker: str,
    limit: int = Query(
        365,
        ge=10,
        le=2000
    )
):

    try:

        df = get_stock_indicators(
            ticker,
            limit
        )

        result = df.copy()

        result["date"] = (
            result["date"]
            .dt.strftime(
                "%Y-%m-%d"
            )
        )

        columns = [
            "date",
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
        ]

        result = result[
            columns
        ]

        # Replace infinity values
        result = result.replace(
            [
                np.inf,
                -np.inf
            ],
            np.nan
        )

        # Replace NaN with None so FastAPI
        # can safely return valid JSON.
        result = result.astype(
            object
        ).where(
            result.notna(),
            None
        )

        return result.to_dict(
            orient="records"
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )