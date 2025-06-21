import os
import uuid
from datetime import datetime
from supabase import create_client
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ELASTIC_URL = os.getenv("ELASTIC_URL", "http://localhost:9200")
es = Elasticsearch(ELASTIC_URL)

def log_supabase(event_type, query, request):
    try:
        supabase.table("search_logs").insert({
            "user_id": request.headers.get("X-User-ID", "anonymous"),
            "channel": request.headers.get("X-Channel", "NA"),
            "type": event_type,
            "query": query,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        print(f"[Supabase] Logging failed: {e}")

def store_redirect(original_url, content_type, metadata):
    guid = str(uuid.uuid4())
    try:
        supabase.table("redirects").insert({
            "guid": guid,
            "original_url": original_url,
            "type": content_type,
            "metadata": metadata,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        print(f"[Supabase] Redirect logging failed: {e}")

    base_domain = os.getenv("BASE_DOMAIN", "https://yourdomain.com")
    return guid, f"{base_domain}/r/{guid}"

def log_elk(index, data):
    try:
        es.index(index=index, body=data)
    except Exception as e:
        print(f"[ELK] Logging failed: {e}")