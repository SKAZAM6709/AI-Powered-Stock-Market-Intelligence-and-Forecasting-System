from fastapi import (
    APIRouter,
    Query,
)

from ..services.market_service import (
    get_market_overview
)


router = APIRouter(
    prefix="/market",
    tags=["Market"],
)


@router.get("/overview")
def market_overview(
    limit: int = Query(
        5,
        ge=1,
        le=20
    )
):
    return get_market_overview(
        limit
    )