from fastapi import APIRouter, Request
from app.services.hotellook import search_hotels
from app.utils.logger import log_supabase, store_redirect
from app.utils.supabase import get_affiliates_by_type_and_priority

router = APIRouter()

@router.get("/search/hotels")
async def hotels(request: Request, location: str, checkin: str, checkout: str, adults: int = 1, children: int = 0, currency: str = "USD", limit: int = 10):
    query = {
        "location": location,
        "checkin": checkin,
        "checkout": checkout,
        "adults": adults,
        "children": children,
        "currency": currency,
        "limit": limit
    }
    log_supabase("search_hotels", query, request)

    affiliates = await get_affiliates_by_type_and_priority("hotel")
    all_results = []

    for affiliate in affiliates:
        results = await search_hotels(location, checkin, checkout, adults, children, currency, limit)
        if results:
            for hotel in results:
                guid, safe_url = store_redirect(hotel["affiliate_link"], "hotel", hotel)
                hotel["redirect_url"] = safe_url
                hotel["affiliate_provider"] = affiliate["provider_name"]
            all_results.extend(results)
            break

    return all_results or {"error": "No results found from any affiliate"}
