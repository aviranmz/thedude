import httpx
import os

API_KEY = os.getenv("SKYSCANNER_API_KEY")
API_HOST = "skyscanner44.p.rapidapi.com"
API_URL = f"https://{API_HOST}/search"

async def search_flights(origin, destination, date, passengers):
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    params = {
        "adults": passengers,
        "origin": origin,
        "destination": destination,
        "departureDate": date,
        "currency": "USD"
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get(API_URL, headers=headers, params=params)
        return res.json()