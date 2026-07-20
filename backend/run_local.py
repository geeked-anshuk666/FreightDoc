"""Start FreightDoc's FastAPI service reliably on local Windows machines.

psycopg's async implementation requires the selector event loop on Windows.
This wrapper sets that policy before Uvicorn starts its reloader or application
loop. Linux deployment environments keep their normal asyncio configuration.
"""

from __future__ import annotations

import asyncio
import os
import sys

if sys.platform == "win32":  # pragma: no cover - platform-specific bootstrap
    selector_policy = getattr(asyncio, "WindowsSelectorEventLoopPolicy", None)
    if selector_policy is not None:
        asyncio.set_event_loop_policy(selector_policy())

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
