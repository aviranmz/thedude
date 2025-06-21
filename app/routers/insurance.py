from fastapi import APIRouter, Request
from app.services.insurance import search_insurance
from app.utils.logger import log_supabase, store_redirect
from app.utils.supabase import get_affiliates_by_type_and_priority

router = APIRouter()

@router.get("/search/insurance")
async def insurance(request: Request, destination: str, start: str, end: str):
    query = {"destination": destination, "start": start, "end": end}
    log_supabase("search_insurance", query, request)

    affiliates = await get_affiliates_by_type_and_priority("insurance")
    all_results = []

    for affiliate in affiliates:
        results = await search_insurance(destination, start, end, affiliate)
        if results:
            for plan in results:
                guid, safe_url = store_redirect(plan["affiliate_link"], "insurance", plan)
                plan["redirect_url"] = safe_url
                plan["affiliate_provider"] = affiliate["provider_name"]
            all_results.extend(results)
            break

    return all_results or {"error": "No results found from any affiliate"}