import os
import httpx
import logging

async def call_trip_api(info):
    origin = info.get("origin")
    destination = info.get("destination")
    dates = info.get("dates", {})
    depart_date = dates.get("start")
    return_date = dates.get("end")
    adults = info.get("adults", 1)
    children = info.get("children", 0)

    base_url = os.getenv("BASE_DOMAIN", "https://yourdomain.com")
    
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY', 'your_api_key')}",
        "Content-Type": "application/json"
    }

    flight_results = []
    hotel_results = []

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Call /search/flights
        if origin and destination and depart_date:
            flight_params = {
                "origin": origin,
                "destination": destination,
                "date": depart_date,
                "return_date": return_date or ""
            }
            try:
                flight_resp = await client.get(f"{base_url}/search/flights", params=flight_params, headers=headers)
                flight_results = flight_resp.json() if flight_resp.status_code == 200 else []
            except Exception as e:
                logging.error(f"Flight search failed: {e}")

        # Call /search/hotels
        if destination and depart_date and return_date:
            hotel_params = {
                "location": destination,
                "checkin": depart_date,
                "checkout": return_date,
                "adults": adults,
                "children": children,
                "currency": "EUR",
                "limit": 5
            }
            try:
                hotel_resp = await client.get(f"{base_url}/search/hotels", params=hotel_params, headers=headers)
                hotel_results = hotel_resp.json() if hotel_resp.status_code == 200 else []
            except Exception as e:
                logging.error(f"Hotel search failed: {e}")

    # Format a response
    if not flight_results and not hotel_results:
        return {"formatted_reply": "No flights or hotels found for your request."}

    reply_parts = []

    # ✈️ Flights
    if isinstance(flight_results, list) and flight_results:
        reply_parts.append("✈️ *Top Flight Option*")
        top_flight = flight_results[0]
        reply_parts.append(f"{top_flight['origin']} → {top_flight['destination']}")
        reply_parts.append(f"Price: {top_flight['price']} {top_flight['currency']}")
        if top_flight.get("departure_date"):
            reply_parts.append(f"Departure: {top_flight['departure_date']}")
        if top_flight.get("return_date"):
            reply_parts.append(f"Return: {top_flight['return_date']}")
        if top_flight.get("redirect_url"):
            reply_parts.append(f"[🔗 Book this flight]({top_flight['redirect_url']})")

    # 🏨 Hotels
    if isinstance(hotel_results, list) and hotel_results:
        reply_parts.append("\n🏨 *Top Hotels in Milan*")
        for hotel in hotel_results[:3]:
            name = hotel.get("hotelName") or hotel.get("name", "Hotel")
            price = hotel.get("priceFrom", "N/A")
            currency = hotel.get("currency", "EUR")
            link = hotel.get("redirect_url", "#")
            reply_parts.append(f"• {name} - {price} {currency} [Book]({link})")

    formatted_reply = "\n".join(reply_parts) or "Sorry, no results found."

    return {
        "formatted_reply": formatted_reply,
        "flights": flight_results,
        "hotels": hotel_results
    }


