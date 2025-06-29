from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def get_user_preferences(user_id):
    if not user_id:
        return {}
    res = supabase.table("user_preferences").select("prefs").eq("user_id", user_id).execute()
    if res.data:
        return res.data[0].get("prefs", {})
    return {}

async def save_user_preferences(user_id, prefs):
    if not user_id:
        return
    supabase.table("user_preferences").update({"prefs": prefs}).eq("user_id", user_id).execute()

async def log_interaction(user_id, message, direction, channel="telegram"):
    if not user_id:
        return
    log_entry = {
        "user_id": user_id,
        "type": direction,
        "query": {"message": message},
        "channel": channel
    }
    supabase.table("search_logs").insert(log_entry).execute()
