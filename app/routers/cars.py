from fastapi import APIRouter, Request
from datetime import datetime, timedelta
from app.services.searchcars import search_cars
from app.utils.logger import log_supabase, store_redirect
from app.utils.supabase import get_affiliates_by_type_and_priority
import logging

router = APIRouter()

@router.get("/search/cars")
async def cars(
    request: Request,
    pickup_iata: str,
    dropoff_iata: str,
    pickup_name: str,
    dropoff_name: str = "",
    pickup_lat: float = 0.0,
    pickup_lng: float = 0.0,
    dropoff_lat: float = 0.0,
    dropoff_lng: float = 0.0,
    date: str = "",           # format: YYYY-MM-DD
    return_date: str = ""     # format: YYYY-MM-DD (optional)
):
    # Default dropoff values
    dropoff_name = dropoff_name or pickup_name
    dropoff_lat = dropoff_lat or pickup_lat
    dropoff_lng = dropoff_lng or pickup_lng

    # Default return date = +5 days
    if not return_date and date:
        try:
            pickup_dt = datetime.strptime(date, "%Y-%m-%d")
            return_date = (pickup_dt + timedelta(days=5)).strftime("%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD."}

    query = {
        "pickup_iata": pickup_iata,
        "dropoff_iata": dropoff_iata,
        "pickup_name": pickup_name,
        "dropoff_name": dropoff_name,
        "pickup_lat": pickup_lat,
        "pickup_lng": pickup_lng,
        "dropoff_lat": dropoff_lat,
        "dropoff_lng": dropoff_lng,
        "date": date,
        "return_date": return_date
    }

    logging.info(f"Search cars query: {query}")
    log_supabase("search_cars", query, request)

    affiliates = await get_affiliates_by_type_and_priority("car")
    all_results = []

    logging.info(f"Found {len(affiliates)} affiliates for car rentals")
    for affiliate in affiliates:
        results = await search_cars(query, affiliate)
        logging.info(f"Affiliate {affiliate['provider_name']} returned {len(results)} results")
        logging.debug(f"Results from {affiliate['provider_name']}: {results}")  
        if results:
            for car in results:
                guid, safe_url = store_redirect(car["affiliate_link"], "car", car)
                car["redirect_url"] = safe_url
                car["affiliate_provider"] = affiliate["provider_name"]
            all_results.extend(results)
            break

    return all_results or {"error": "No results found from any affiliate"}
