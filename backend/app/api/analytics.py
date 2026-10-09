from fastapi import (
    APIRouter,
    HTTPException,
)

from ..services.analytics_service import (
    get_model_metrics,
    get_best_models,
    get_analytics_overview,
    get_sentiment_model_comparison,
    get_sentiment_confusion_matrices,
    get_sentiment_classification_reports,
    get_sentiment_distribution,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


# =================================================
# FORECAST MODEL METRICS
# =================================================

@router.get("/models")
def model_metrics():

    try:

        return get_model_metrics()

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
# BEST FORECAST MODELS
# =================================================

@router.get("/best-models")
def best_models():

    try:

        return get_best_models()

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
# ANALYTICS OVERVIEW
# =================================================

@router.get("/overview")
def analytics_overview():

    try:

        return get_analytics_overview()

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
# SENTIMENT MODEL COMPARISON
# =================================================

@router.get("/sentiment/models")
def sentiment_model_comparison():

    try:

        return get_sentiment_model_comparison()

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
# SENTIMENT CONFUSION MATRIX
# =================================================

@router.get("/sentiment/confusion-matrix")
def sentiment_confusion_matrix():

    try:

        return get_sentiment_confusion_matrices()

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
# SENTIMENT CLASSIFICATION REPORT
# =================================================

@router.get("/sentiment/classification-report")
def sentiment_classification_report():

    try:

        return get_sentiment_classification_reports()

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
# SENTIMENT DISTRIBUTION
# =================================================

@router.get("/sentiment/distribution")
def sentiment_distribution():

    try:

        return get_sentiment_distribution()

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
            detail=str(error)
        )