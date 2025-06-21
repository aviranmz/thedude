from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def get_affiliates_by_type_and_priority(affiliate_type: str):
    try:
        response = supabase.table("affiliate_templates") \
            .select("*") \
            .eq("type", affiliate_type) \
            .order("priority", desc=False) \
            .execute()
        return response.data or []
    except Exception as e:
        print(f"Error fetching affiliates: {e}")
        return []
