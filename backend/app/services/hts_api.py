import asyncio
import logging
from datetime import datetime, timezone
import httpx
from app.config import get_settings
from app.models import TariffData

logger = logging.getLogger("freightdoc.hts")
FALLBACK_TARIFFS = {"US-DE": 4.0, "US-GB": 4.0, "US-IN": 10.0, "US-JP": 5.0, "US-CA": 3.5, "US-AU": 5.0, "IN-US": 4.0, "CN-EU": 6.0}


async def lookup_usitc(hs_code: str, corridor: str, request_id: str) -> TariffData:
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=get_settings().request_timeout_seconds) as client:
                response = await client.get("https://hts.usitc.gov/reststop/search", params={"keyword": hs_code})
                response.raise_for_status()
                logger.info("request_id=%s source=USITC attempt=%s status=ok", request_id, attempt + 1)
                return TariffData(duty_rate=None, source="USITC HTS", additional_flags=["HTS search returned; confirm the final rate at tariff-line level."], retrieved_at=datetime.now(timezone.utc))
        except httpx.HTTPError:
            await asyncio.sleep(0.25 * 2**attempt)
    return TariffData(duty_rate=FALLBACK_TARIFFS[corridor], source="fallback tariff dataset", additional_flags=["USITC unavailable; illustrative demo fallback."], retrieved_at=datetime.now(timezone.utc), fallback_used=True)
