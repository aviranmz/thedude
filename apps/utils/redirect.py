import uuid
from datetime import datetime, timedelta
from supabase import create_client
import os

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_redirect(original_url: str, type_: str, metadata: dict = None, expires_in_days: int = 7, max_clicks: int = 10):
    guid = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

    supabase.table("redirects").insert({
        "guid": guid,
        "original_url": original_url,
        "type": type_,
        "metadata": metadata or {},
        "clicks": 0,
        "max_clicks": max_clicks,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    return guid
