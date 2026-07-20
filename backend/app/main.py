import logging
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("freightdoc")
app = FastAPI(title="FreightDoc API", version="0.2.0", docs_url="/docs", redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID", "Retry-After"],
)


@app.middleware("http")
async def request_correlation(request: Request, call_next):
    request.state.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    content_length = request.headers.get("content-length")
    # Multipart intake has a separate 40 MiB aggregate cap. Other API bodies
    # never need to be larger than one MiB because models cap every text field.
    max_bytes = 40 * 1024 * 1024 if "/documents" in request.url.path else 1 * 1024 * 1024
    if content_length and content_length.isdigit() and int(content_length) > max_bytes:
        return JSONResponse(
            status_code=413,
            content={"detail": {"code": "REQUEST_TOO_LARGE", "message": "The request exceeds the safe size limit."}},
            headers={"X-Request-ID": request.state.request_id},
        )
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    # The API serves JSON/PDF data only; lock down browser behaviour even when
    # it is accessed directly rather than through the Vercel application.
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'; base-uri 'none'")
    if request.url.scheme == "https":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    logger.info("request_id=%s method=%s path=%s status=%s", request.state.request_id, request.method, request.url.path, response.status_code)
    return response


@app.get("/health")
async def health():
    settings = get_settings()
    return {
        "status": "ok",
        "service": "freightdoc-api",
        "version": app.version,
        "persistence_configured": bool(settings.database_url),
        "clerk_verification_configured": settings.clerk_auth_configured,
    }


app.include_router(router)
