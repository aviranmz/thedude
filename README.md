python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

ENV=local uvicorn main:app --reload


/Users/aviranm/personal/Aviran/thedude/static/out.txt

https://dspy.ai/


curl -H "Authorization: Bearer supersecretkey123" \
"https://thedude-production.up.railway.app/search/hotels?location=rome&checkin=2025-07-01&checkout=2025-07-05&adults=2&children=1&currency=EUR&limit=5"

curl -H "Authorization: Bearer supersecretkey123" \
"https://thedude-production.up.railway.app/search/flights?origin=TLV&destination=MXP&date=02022026"

curl -H "Authorization: Bearer supersecretkey123" \
"https://thedude-production.up.railway.app/search/flights?origin=MOW&destination=MXP&date=01012026&return_date=02022026"

curl -H "Authorization: Bearer supersecretkey123" \
"https://thedude-production.up.railway.app/search/esim?destination=france"