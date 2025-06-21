from fastapi import APIRouter, Request
from app.services.rentalcars import search_cars
from app.utils.logger import log_supabase, store_redirect
from app.utils.supabase import get_affiliates_by_type_and_priority

router = APIRouter()

@router.get("/search/cars")
async def cars(request: Request, pickup: str, dropoff: str, date: str):
    query = {"pickup": pickup, "dropoff": dropoff, "date": date}
    log_supabase("search_cars", query, request)

    affiliates = await get_affiliates_by_type_and_priority("car")
    all_results = []

    for affiliate in affiliates:
        results = await search_cars(pickup, dropoff, date, affiliate)
        if results:
            for car in results:
                guid, safe_url = store_redirect(car["affiliate_link"], "car", car)
                car["redirect_url"] = safe_url
                car["affiliate_provider"] = affiliate["provider_name"]
            all_results.extend(results)
            break

    return all_results or {"error": "No results found from any affiliate"}
