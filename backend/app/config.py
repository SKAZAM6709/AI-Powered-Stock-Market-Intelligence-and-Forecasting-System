from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Main project folder:
# stock_market_ai/
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):

    app_name: str = "StockAI Intelligence"
    app_version: str = "1.0.0"
    app_env: str = "development"

    # Database
    database_url: str = "sqlite:///./stockai.db"

    # Dataset paths
    stock_data_path: str = "data/raw/all_stocks_5yr.csv"
    news_data_path: str = "data/raw/financial_news.csv"

    model_config = SettingsConfigDict(
        env_file=str(
            PROJECT_ROOT
            / "backend"
            / ".env"
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def stock_file(self) -> Path:
        return (
            PROJECT_ROOT
            / self.stock_data_path
        )

    @property
    def news_file(self) -> Path:
        return (
            PROJECT_ROOT
            / self.news_data_path
        )


settings = Settings()