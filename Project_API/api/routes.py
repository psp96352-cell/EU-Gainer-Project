from fastapi import APIRouter
from services.gainer_service import calculate_gainers

router = APIRouter()

@router.get("/get_gainers")
def get_gainers(interval_minutes: int = 5, min_gain: float = 2.0, top_n: int = 10):
    return calculate_gainers(interval_minutes, min_gain, top_n)
