from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["APIx Price Indices"])

class IndexResponse(BaseModel):
    date: str
    apix: float
    weekly_ma: float

@router.get("/index", response_model=list[IndexResponse])
def get_daily_index():
    """
    Exposes daily calculated APIx indices with rolling averages to endpoints.
    """
    return [
        {"date": "2024-05-01", "apix": 100.00, "weekly_ma": 100.00},
        {"date": "2024-05-13", "apix": 106.12, "weekly_ma": 102.34},
        {"date": "2024-05-22", "apix": 114.23, "weekly_ma": 108.45}
    ]
