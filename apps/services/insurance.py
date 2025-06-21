import urllib.parse

async def search_insurance(destination: str, start: str, end: str, affiliate: dict):
    try:
        url = affiliate["template_url"].format(
            destination=urllib.parse.quote_plus(destination),
            start=urllib.parse.quote_plus(start),
            end=urllib.parse.quote_plus(end)
        )
        return [{
            "name": f"Travel Insurance to {destination}",
            "affiliate_link": url,
            "price": None
        }]
    except Exception:
        return []