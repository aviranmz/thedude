# app/routers/flights.py
from fastapi import APIRouter, Request
from app.services.skyscanner import search_flights
from app.utils.logger import log_supabase, store_redirect
from app.utils.supabase import get_affiliates_by_type_and_priority

router = APIRouter()

@router.get("/flights")
async def flights(request: Request, origin: str, destination: str, date: str):
    query = {"origin": origin, "destination": destination, "date": date}
    log_supabase("search_flights", query, request)
    
    affiliates = await get_affiliates_by_type_and_priority("flight")
    all_results = []

    for affiliate in affiliates:
        try:
            results = await search_flights(origin, destination, date, affiliate)
            for flight in results:
                guid, safe_url = store_redirect(flight["affiliate_link"], "flight", flight)
                flight["redirect_url"] = safe_url
                flight["affiliate_provider"] = affiliate["provider_name"]
            all_results.extend(results)
        except Exception:
            continue
    return all_results