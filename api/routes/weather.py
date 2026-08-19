from fastapi import APIRouter, Depends
from api.schemas import WeatherResponse
from api.auth import current_user
from core.weather import get_weather

router = APIRouter()


@router.get("/weather/cities", response_model=WeatherResponse)
def weather_cities(user=Depends(current_user)):
    result = get_weather()
    return WeatherResponse(**result)