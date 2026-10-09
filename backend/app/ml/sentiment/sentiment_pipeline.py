from .text_cleaner import (
    clean_text,
)

from .vader_model import (
    analyze_vader,
)

from .finbert_model import (
    analyze_finbert,
)


def analyze_sentiment(
    text: str,
    model_name: str = "vader"
) -> dict:
    """
    Analyze financial text sentiment.

    Supported models:
    - vader
    - finbert
    """

    cleaned_text = clean_text(
        text
    )

    if not cleaned_text:
        raise ValueError(
            "Text cannot be empty."
        )

    model_name = (
        model_name
        .strip()
        .lower()
    )

    # =========================================
    # VADER
    # =========================================

    if model_name == "vader":

        result = analyze_vader(
            cleaned_text
        )

        return {
            "original_text":
                text,

            "cleaned_text":
                cleaned_text,

            **result,

            "model":
                "VADER"
        }

    # =========================================
    # FINBERT
    # =========================================

    if model_name == "finbert":

        result = analyze_finbert(
            cleaned_text
        )

        return {
            "original_text":
                text,

            "cleaned_text":
                cleaned_text,

            **result,

            "model":
                "FinBERT"
        }

    # =========================================
    # INVALID MODEL
    # =========================================

    raise ValueError(
        "Unsupported sentiment model. "
        "Use 'vader' or 'finbert'."
    )