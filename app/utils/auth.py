from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import os

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # ✅ Allow unauthenticated OPTIONS requests for CORS
        if request.method == "OPTIONS":
            return await call_next(request)

        # ✅ Allow public paths without auth
        if request.url.path.startswith((
            "/docs", "/openapi.json", "/r", "/home.html", "/static"
        )):
            return await call_next(request)

        # 🔐 Check Bearer Auth
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")

        token = auth_header.split(" ")[1]
        if token != os.getenv("API_KEY"):
            raise HTTPException(status_code=403, detail="Forbidden")

        return await call_next(request)
