import asyncio
import logging
from datetime import datetime, timezone
import httpx
from app.config import get_settings
from app.models import TariffData
from app.services.hts_api import FALLBACK_TARIFFS

logger = logging.getLogger("freightdoc.comtrade")


async def lookup_comtrade(hs_code: str, corridor: str, request_id: str) -> TariffData:
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=get_settings().request_timeout_seconds) as client:
                response = await client.get("https://comtradeapi.un.org/public/v1/preview/C/A/HS", params={"cmdCode": hs_code[:6], "flowCode": "M", "period": str(datetime.now().year - 1), "reporterCode": "0", "partnerCode": "0", "maxRecords": "1"})
                response.raise_for_status()
                logger.info("request_id=%s source=UN_COMTRADE attempt=%s status=ok", request_id, attempt + 1)
                return TariffData(duty_rate=None, source="UN Comtrade public-v1", additional_flags=["Bilateral trade-data context only; it is not a duty-rate authority."], retrieved_at=datetime.now(timezone.utc))
        except httpx.HTTPError:
            await asyncio.sleep(0.25 * 2**attempt)
    return TariffData(duty_rate=FALLBACK_TARIFFS[corridor], source="fallback tariff dataset", additional_flags=["UN Comtrade unavailable; illustrative demo fallback."], retrieved_at=datetime.now(timezone.utc), fallback_used=True)
