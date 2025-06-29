import httpx
import logging
import json
from datetime import datetime, timedelta

SKY_SCRAPPER_API_URL = "https://sky-scrapper.p.rapidapi.com/api/v1/cars/searchCars"

async def search_cars(params: dict, affiliate: dict):
    try:
        provider = affiliate.get("provider_name")

        if provider != "sky-scrapper":
            logging.warning(f"Unsupported provider: {provider}")
            return []

        headers = {
            "x-rapidapi-host": "sky-scrapper.p.rapidapi.com",
            "x-rapidapi-key": "3fc12471f3mshadd55885ef89405p198b3bjsne3e72c47d534"
        }

        pick_up_entity_id = affiliate.get("pickup_entity_id", "27537542")
        date = params["date"]
        pickup_time = "10:00"

        url = (
            f"{SKY_SCRAPPER_API_URL}"
            f"?pickUpEntityId={pick_up_entity_id}"
            f"&pickUpDate={date}"
            f"&pickUpTime={pickup_time}"
            f"&currency=EUR"
            f"&countryCode=IT"
            f"&market=it-IT"
        )

        logging.info(f"[Sky-Scrapper] Request: {url}")
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            logging.warning(f"[Sky-Scrapper] RAW resp.text (first 500 chars): {resp.text[:500]}")

            try:
                data = resp.json()
            except Exception:
                data = json.loads(resp.text)

            # 🔁 Double-parse if data is still a string
            if isinstance(data, str):
                logging.info("[Sky-Scrapper] Double-parsing JSON response")
                data = json.loads(data)

        if not isinstance(data, dict):
            raise ValueError(f"Unexpected data type: {type(data)}")

        results = []
        quotes = data.get("data", {}).get("quotes", [])
        for offer in quotes:
            results.append({
                "price": offer.get("tot_price"),  # ✅ Just a float, no .get("amount")
                "currency": offer.get("currency", "EUR"),
                "car_model": offer.get("sipp", "Unknown"),  # or vendor name or vehicle type
                "pickup_location": offer.get("loc", {}).get("pu", "PU"),
                "dropoff_location": offer.get("loc", {}).get("do", "DO"),
                "affiliate_link": offer.get("deeplink", ""),
                "provider": provider
            })

        return results

    except Exception as e:
        logging.error(f"[search_cars] API error with provider {provider}: {e}")
        return []
