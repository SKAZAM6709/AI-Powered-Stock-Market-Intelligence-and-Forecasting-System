from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings

from .api import (
    stocks,
    market,
    forecast,
    analytics,
    sentiment,
)


# =================================================
# CREATE FASTAPI APPLICATION
# =================================================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-Powered Stock Market Intelligence "
        "and Forecasting System using Machine Learning, "
        "Time-Series Analysis, Deep Learning, "
        "and Financial News Sentiment Analysis."
    ),
)


# =================================================
# CORS CONFIGURATION
# =================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =================================================
# ROOT ENDPOINT
# =================================================

@app.get("/")
def root():
    """
    Basic API status endpoint.
    """

    return {
        "message":
            "StockAI Intelligence API is running",

        "app_name":
            settings.app_name,

        "version":
            settings.app_version,

        "environment":
            settings.app_env,
    }


# =================================================
# HEALTH CHECK
# =================================================

@app.get("/health")
def health_check():
    """
    Health-check endpoint.
    """

    return {
        "status": "healthy",
        "service": settings.app_name,
    }


# =================================================
# REGISTER API ROUTERS
# =================================================

# -----------------------------
# Stocks
# -----------------------------

app.include_router(
    stocks.router,
    prefix="/api"
)


# -----------------------------
# Market Overview
# -----------------------------

app.include_router(
    market.router,
    prefix="/api"
)


# -----------------------------
# Forecasting
# -----------------------------

app.include_router(
    forecast.router,
    prefix="/api"
)


# -----------------------------
# Model Analytics
# -----------------------------

app.include_router(
    analytics.router,
    prefix="/api"
)


# -----------------------------
# Sentiment Analysis
# -----------------------------

app.include_router(
    sentiment.router,
    prefix="/api"
)