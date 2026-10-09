from pydantic import (
    BaseModel,
    Field,
)


class SentimentRequest(
    BaseModel
):
    text: str = Field(
        ...,
        min_length=1,
        description=(
            "Financial news headline "
            "or article text."
        )
    )