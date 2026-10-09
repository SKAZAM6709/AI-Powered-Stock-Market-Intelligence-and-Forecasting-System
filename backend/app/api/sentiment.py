from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from ..schemas.sentiment import (
    SentimentRequest,
)

from ..services.sentiment_service import (
    get_text_sentiment,
    get_sentiment_dataset_info,
    get_news_records,
    get_sentiment_summary,
    get_ticker_sentiment,
)


router = APIRouter(
    prefix="/sentiment",
    tags=["Sentiment"],
)


# =================================================
# MANUAL TEXT ANALYSIS
# =================================================

@router.post("/analyze")
def analyze_news_sentiment(
    request: SentimentRequest,

    model: str = Query(
        "vader",
        description=(
            "Sentiment model: vader or finbert"
        )
    )
):

    try:

        return get_text_sentiment(
            text=request.text,
            model_name=model
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except RuntimeError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Sentiment analysis failed: "
                f"{str(error)}"
            )
        )


# =================================================
# DATASET INFO
# =================================================

@router.get("/info")
def sentiment_dataset_info():

    try:

        return get_sentiment_dataset_info()

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# =================================================
# NEWS
# =================================================

@router.get("/news")
def sentiment_news(
    limit: int = Query(
        50,
        ge=1,
        le=500
    )
):

    try:

        return get_news_records(
            limit=limit
        )

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# =================================================
# SUMMARY
# =================================================

@router.get("/summary")
def sentiment_summary():

    try:

        return get_sentiment_summary()

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# =================================================
# TICKER SENTIMENT
# =================================================

@router.get("/ticker/{ticker}")
def ticker_sentiment(
    ticker: str,

    limit: int = Query(
        50,
        ge=1,
        le=200
    )
):

    try:

        return get_ticker_sentiment(
            ticker=ticker,
            limit=limit
        )

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )