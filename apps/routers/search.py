from fastapi import APIRouter, Request
from app.services.hotellook import search_hotels
from app.utils.logger import log_supabase, store_redirect

router = APIRouter()

@router.get("/hotels")
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
    results = await search_hotels(location, checkin, checkout, adults, children, currency, limit)

    for hotel in results:
        guid, safe_url = store_redirect(hotel["affiliate_link"], "hotel", hotel)
        hotel["redirect_url"] = safe_url

    return results