import time
from typing import Dict, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

# Simple in-memory rate limiter for AI analysis endpoint to prevent quota abuse and DoS
class RateLimiter:
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.history: Dict[str, list] = {}

    def is_allowed(self, client_ip: str) -> Tuple[bool, int]:
        now = time.time()
        timestamps = self.history.get(client_ip, [])
        # Filter timestamps within window
        valid_timestamps = [t for t in timestamps if now - t < self.window_seconds]
        self.history[client_ip] = valid_timestamps

        if len(valid_timestamps) >= self.max_requests:
            retry_after = int(self.window_seconds - (now - valid_timestamps[0]))
            return False, max(1, retry_after)

        self.history[client_ip].append(now)
        return True, 0

ai_rate_limiter = RateLimiter(max_requests=5, window_seconds=60)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Rate limiting on AI analysis endpoint
        if request.url.path == "/api/v1/ai/analyze" and request.method == "POST":
            client_ip = request.client.host if request.client else "unknown"
            allowed, retry_after = ai_rate_limiter.is_allowed(client_ip)
            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": f"Demasiadas solicitudes de análisis. Por favor espera {retry_after} segundos antes de volver a consultar a Gemini.",
                        "error_code": "RATE_LIMIT_EXCEEDED",
                        "retry_after_seconds": retry_after
                    },
                    headers={"Retry-After": str(retry_after)}
                )

        # 2. Body size limit check for IoT ingestion (64 KB max)
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 65536:
            return JSONResponse(
                status_code=413,
                content={"detail": "Payload demasiado grande. Límite máximo: 64 KB."}
            )

        # 3. Process request
        response: Response = await call_next(request)

        # 4. Inject OWASP Recommended Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response
