import urllib.parse

async def search_cars(pickup: str, dropoff: str, date: str, affiliate: dict):
    try:
        url = affiliate["template_url"].format(
            pickup=urllib.parse.quote_plus(pickup),
            dropoff=urllib.parse.quote_plus(dropoff),
            date=urllib.parse.quote_plus(date)
        )
        return [{
            "name": f"Car Rental - {pickup} to {dropoff}",
            "affiliate_link": url,
            "price": None
        }]
    except Exception:
        return []