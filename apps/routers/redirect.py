from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from app.utils.logger import supabase, log_elk
from datetime import datetime

router = APIRouter()

@router.get("/r/{guid}")
async def redirect_guid(guid: str, request: Request):
    result = supabase.table("redirects").select("*").eq("guid", guid).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Invalid link")

    redirect_data = result.data[0]
    now = datetime.utcnow()

    # Check expiration
    if redirect_data.get("expires_at") and now > datetime.fromisoformat(redirect_data["expires_at"]):
        raise HTTPException(status_code=410, detail="Link expired")

    # Check max clicks
    clicks = redirect_data.get("clicks", 0)
    max_clicks = redirect_data.get("max_clicks")
    if max_clicks is not None and clicks >= max_clicks:
        raise HTTPException(status_code=410, detail="Click limit reached")

    # Update clicks
    supabase.table("redirects").update({"clicks": clicks + 1}).eq("guid", guid).execute()

    # Log event
    log_elk("redirects", {
        "guid": guid,
        "ip": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "timestamp": now.isoformat()
    })

    return RedirectResponse(redirect_data["original_url"], status_code=302)
