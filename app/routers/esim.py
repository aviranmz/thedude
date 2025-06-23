from fastapi import APIRouter, Request
from app.utils.logger import log_supabase, store_redirect
from app.utils.supabase import get_affiliates_by_type_and_priority

router = APIRouter()

@router.get("/search/esim")
async def search_esim(request: Request, destination: str):
    query = {"country": destination}
    log_supabase("search_esim", query, request)

    # Get your eSIM affiliate template from Supabase (e.g. Airalo)
    affiliates = await get_affiliates_by_type_and_priority("esim")
    if not affiliates:
        return {"error": "No affiliate available for eSIM"}

    affiliate = affiliates[0]
    base_url = affiliate["template_url"]  # Example: https://www.airalo.com/?irclickid=xxxx&utm...

    # Format: https://www.airalo.com/france-esim?irclickid=...
    country_slug = destination.lower().replace(" ", "-")
    full_url = base_url.replace("https://www.airalo.com", f"https://www.airalo.com/{country_slug}-esim")

    guid, safe_url = store_redirect(full_url, "esim", {"country": destination})

    return {
        "country": destination,
        "affiliate_provider": affiliate["provider_name"],
        "redirect_url": safe_url
    }
