from nltk.sentiment import (
    SentimentIntensityAnalyzer,
)


_analyzer = None


def get_analyzer():
    """
    Create the VADER analyzer once
    and reuse it.
    """

    global _analyzer

    if _analyzer is None:

        try:

            _analyzer = (
                SentimentIntensityAnalyzer()
            )

        except LookupError:

            raise RuntimeError(
                "VADER lexicon not found. "
                "Run: "
                "python -m nltk.downloader "
                "vader_lexicon"
            )

    return _analyzer


def analyze_vader(
    text: str
) -> dict:
    """
    Analyze text sentiment using VADER.
    """

    analyzer = get_analyzer()

    scores = analyzer.polarity_scores(
        text
    )

    compound = float(
        scores["compound"]
    )

    # Standard VADER thresholds
    if compound >= 0.05:

        sentiment = "Positive"

    elif compound <= -0.05:

        sentiment = "Negative"

    else:

        sentiment = "Neutral"

    return {
        "sentiment":
            sentiment,

        "compound":
            compound,

        "positive":
            float(
                scores["pos"]
            ),

        "neutral":
            float(
                scores["neu"]
            ),

        "negative":
            float(
                scores["neg"]
            ),
    }