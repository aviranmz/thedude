from fastapi import APIRouter, Request
from app.services.flightlook import search_flights
from app.utils.logger import log_supabase, store_redirect
from app.utils.supabase import get_affiliates_by_type_and_priority
import logging

router = APIRouter()

@router.get("/search/flights")
async def flights(request: Request, origin: str, destination: str, date: str, return_date: str = ""):
    query = {"origin": origin, "destination": destination, "date": date}
    log_supabase("search_flights", query, request)

    affiliates = await get_affiliates_by_type_and_priority("flight")
    logging.info(f"Found {len(affiliates)} affiliates for flights")
    all_results = []
    for affiliate in affiliates:
        results = await search_flights(origin, destination, date, return_date, affiliate)
        logging.info(f"Affiliate {affiliate['provider_name']} returned {len(results)} results")
        if results:
            for flight in results:
                guid, safe_url = store_redirect(flight["affiliate_link"], "flight", flight)
                flight["redirect_url"] = safe_url
                flight["affiliate_provider"] = affiliate["provider_name"]
            all_results.extend(results)
            break

    return all_results or {"error": "No results found from any affiliate"}
