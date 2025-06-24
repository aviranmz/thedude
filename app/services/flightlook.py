import httpx
from datetime import datetime
import logging

API_V1_URL = "https://api.travelpayouts.com/v1/prices/cheap"
API_V2_URL = "https://api.travelpayouts.com/v2/prices/latest"

def parse_date_flexibly(date_str):
    for fmt in ("%d%m%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Date format not recognized: {date_str}")

async def search_flights(origin, destination, date, return_date ="", affiliate ={}):
    headers = {
        "X-Access-Token": affiliate["api_key"]
    }

    try:
        # Format date into YYYY-MM for the API
        depart_date = ""
        depart_return_date = ""

        if date:
            parsed_date = parse_date_flexibly(date)
            depart_date = parsed_date.strftime("%Y-%m")

        if return_date:
            parsed_return_date = parse_date_flexibly(return_date)
            depart_return_date = parsed_return_date.strftime("%Y-%m")

        # Decide which Travelpayouts API to use
        if affiliate.get("provider_url") == "v2":
            url = API_V2_URL
            params = {
                "currency": "usd",
                "period_type": "year",
                "page": 1,
                "limit": 30,
                "show_to_affiliates": True,
                "sorting": "price",
                "trip_class": 0,
                "token": affiliate["api_key"]
            }
        else:
            url = API_V1_URL
            params = {
                "origin": origin,
                "destination": destination,
                "depart_date": depart_date,
                "return_date": depart_return_date,  # Optional for now
                "token": affiliate["api_key"]
            }

        # Call Travelpayouts API
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params, headers=headers)
            data = response.json()

        logging.info(f"Flight API raw response: {data}")
        flights = []

        # Parse v1 response
        if "v1" in url:
            prices_by_dest = data.get("data", {})
            currency = data.get("currency", "USD")

            for dest, offers in prices_by_dest.items():
                for offer_id, flight in offers.items():
                    flights.append({
                        "price": flight.get("price", 0),
                        "currency": currency,
                        "origin": origin,
                        "destination": dest,
                        "departure_date": flight.get("departure_at"),
                        "return_date": flight.get("return_at"),
                        "airline": flight.get("airline"),
                        "flight_number": flight.get("flight_number"),
                        "affiliate_link": f"https://www.aviasales.com/search/{origin}0101{dest}0202"
                    })

        # Parse v2 response
        else:
            currency = data.get("currency", "USD")
            for flight in data.get("data", []):
                flights.append({
                    "price": flight.get("price", 0),
                    "currency": currency,
                    "origin": flight.get("origin"),
                    "destination": flight.get("destination"),
                    "departure_date": flight.get("depart_date"),
                    "affiliate_link": flight.get("link", "")
                })

        logging.info(f"Found {len(flights)} flights for {origin} to {destination} on {date}")
        return flights

    except Exception as e:
        logging.error(f"Flight API error: {e}")
        return []
