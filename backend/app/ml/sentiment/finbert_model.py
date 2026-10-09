import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)


MODEL_NAME = "ProsusAI/finbert"

_tokenizer = None
_model = None


def load_finbert():
    """
    Load FinBERT tokenizer and model once
    and reuse them for future predictions.
    """

    global _tokenizer
    global _model

    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME
        )

    if _model is None:
        _model = (
            AutoModelForSequenceClassification
            .from_pretrained(
                MODEL_NAME
            )
        )

        _model.eval()

    return _tokenizer, _model


def analyze_finbert(
    text: str
) -> dict:
    """
    Analyze financial news sentiment
    using the FinBERT model.
    """

    if not text or not text.strip():
        raise ValueError(
            "Text cannot be empty."
        )

    tokenizer, model = load_finbert()

    # -----------------------------------------
    # Convert text into model input
    # -----------------------------------------

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True,
    )

    # -----------------------------------------
    # Prediction
    # -----------------------------------------

    with torch.no_grad():
        outputs = model(
            **inputs
        )

    # -----------------------------------------
    # Convert logits into probabilities
    # -----------------------------------------

    probabilities = (
        torch.nn.functional.softmax(
            outputs.logits,
            dim=-1
        )[0]
    )

    # -----------------------------------------
    # Read FinBERT labels
    # -----------------------------------------

    id2label = (
        model.config.id2label
    )

    scores = {}

    for index, probability in enumerate(
        probabilities
    ):
        label = str(
            id2label[index]
        ).lower()

        scores[label] = float(
            probability.item()
        )

    # -----------------------------------------
    # Extract probabilities
    # -----------------------------------------

    positive = scores.get(
        "positive",
        0.0
    )

    negative = scores.get(
        "negative",
        0.0
    )

    neutral = scores.get(
        "neutral",
        0.0
    )

    # -----------------------------------------
    # Determine final label
    # -----------------------------------------

    label_scores = {
        "Positive": positive,
        "Negative": negative,
        "Neutral": neutral,
    }

    sentiment = max(
        label_scores,
        key=label_scores.get
    )

    confidence = max(
        label_scores.values()
    )

    # -----------------------------------------
    # Signed sentiment score
    #
    # Positive values = positive sentiment
    # Negative values = negative sentiment
    # Near zero = neutral
    # -----------------------------------------

    compound = (
        positive
        - negative
    )

    return {
        "sentiment":
            sentiment,

        "confidence":
            round(
                confidence,
                6
            ),

        "positive":
            round(
                positive,
                6
            ),

        "neutral":
            round(
                neutral,
                6
            ),

        "negative":
            round(
                negative,
                6
            ),

        "compound":
            round(
                compound,
                6
            ),

        "model":
            "FinBERT"
    }