from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import os

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json") or request.url.path.startswith("/redirect"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")

        token = auth_header.split(" ")[1]
        if token != os.getenv("API_KEY"):
            raise HTTPException(status_code=403, detail="Forbidden")

        return await call_next(request)