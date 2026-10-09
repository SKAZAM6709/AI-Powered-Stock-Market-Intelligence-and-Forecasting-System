import re


def clean_text(text: str) -> str:
    """
    Basic cleaning for financial news text.
    """

    if not text:
        return ""

    text = str(text)

    # Remove URLs
    text = re.sub(
        r"http\S+|www\S+",
        " ",
        text
    )

    # Remove HTML
    text = re.sub(
        r"<.*?>",
        " ",
        text
    )

    # Remove unnecessary whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()