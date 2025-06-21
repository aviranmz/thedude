import httpx

BASE_URL = "https://engine.hotellook.com/api/v2/cache.json"
AFFILIATE_TEMPLATE = "https://www.hotellook.com/hotels/{hotel_id}?marker=615157&checkIn={checkin}&checkOut={checkout}&adults={adults}"

async def search_hotels(location, checkin, checkout, adults, children, currency, limit):
    params = {
        "location": location,
        "checkIn": checkin,
        "checkOut": checkout,
        "adults": adults,
        "children": children,
        "currency": currency,
        "limit": limit,
        "details": 1,
        "photos": 2
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(BASE_URL, params=params)
        data = response.json()
        for hotel in data:
            hotel_id = hotel.get("hotelId")
            hotel["affiliate_link"] = AFFILIATE_TEMPLATE.format(hotel_id=hotel_id, checkin=checkin, checkout=checkout, adults=adults)
        return data