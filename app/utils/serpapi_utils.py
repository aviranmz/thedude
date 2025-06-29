
import os
import httpx

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

async def search_images_and_links(query):
    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "tbm": "isch",
        "api_key": SERPAPI_KEY
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            images = [img["original"] for img in data.get("images_results", [])[:5]]
            return images
        return []
